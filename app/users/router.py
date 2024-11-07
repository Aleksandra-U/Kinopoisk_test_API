from fastapi import APIRouter, Request, Response, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession 

from app.users.dao import UsersDAO
from app.users.models import Users
from app.users.dependencies import get_current_user
from app.dao.dependencies import get_db_session
from app.logger import logger
from app.users.auth import authenticate_user, create_access_token, get_password_hash
from app.exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException, DontMatchPassExceptions
from app.exceptions import NoUserExceptions, ErrorWithRegisterException, ErrorWithEntranceException, ErrorProfileException




router = APIRouter(
    prefix='/auth',
    tags=['Auth & Пользователи'],
)




#аутентификация 
@router.post("/login")
async def login_user(
    request: Request, 
    response: Response, 
    user_name: str = Form(...), 
    password: str = Form(...), 
    session_db: AsyncSession = Depends(get_db_session)
):
    """
    Обработчик для входа пользователя в систему.

    Аргументы:
    - request (Request): Объект запроса.
    - response (Response): Объект ответа, используемый для установки куки.
    - user_name (str): Имя пользователя, полученное из формы.
    - password (str): Пароль, полученный из формы.
    - session_db (AsyncSession): Асинхронная сессия базы данных, используемая для аутентификации.

    Возвращает:
    - dict: Словарь с сообщением об успешной авторизации, если вход выполнен успешно.

    Исключения:
    - IncorrectEmailOrPasswordException: Выдается, если указаны неверные имя пользователя или пароль.
    - Другие исключения: Логируются в случае возникновения ошибки, не связанной с аутентификацией.
    """
    
    try:
        user = await authenticate_user(session_db, user_name, password)
        if not user:
            logger.error(f"Неверный вход: отсутствует пользователь с именем {user_name}") 
            raise IncorrectEmailOrPasswordException

        access_token = create_access_token({'sub': str(user.id)}) 

        response.set_cookie('booking_access_token', access_token, httponly=True)

        return {"message": "Вы успешно авторизовались!"}

    except IncorrectEmailOrPasswordException: 
        raise IncorrectEmailOrPasswordException

    except Exception as e: 
        logger.error(f"Ошибка при попытке входа: {str(e)}") 
        return ErrorWithEntranceException


#регистрация
@router.post("/register") 
async def register_user(
    request: Request, 
    user_name: str = Form(...), 
    password: str = Form(...), 
    password_repeat: str = Form(...),
    session_db: AsyncSession = Depends(get_db_session)
): 
    """
    Эндпоинт для регистрации нового пользователя

    Параметры:
    - request: объект запроса
    - user_name: имя пользователя, предоставленное при регистрации. Должно быть уникальным
    - password: пеароль, выбранный пользователем
    - password_repeat: повторный ввод пароля для проверки (должен совпадать с password)
    - session_db: асинхронная сессия базы данных, используемая для взаимодействия с базой данных

    В процессе регистрации проверяются  условия:
    - проверка на существование пользователя с данным именем: если пользователь с 
    таким именем уже зарегистрирован, будет вызван UserAlreadyExistsException
    - проверка совпадения паролей: если password и password_repeat не совпадают, 
    будет вызван DontMatchPassExceptions.
    - если все проверки пройдены, пароль хешируется и пользователь добавляется в базу данных

    На выходе возвращается сообщение о успешной регистрации или ошибка, если что-то пошло не так.
    """
    try:
        existing_user = await UsersDAO.find_one_or_none(session_db, user_name=user_name)
        if existing_user:
            logger.error(f"Попытка регистрации существующего пользователя: {user_name}") 
            raise UserAlreadyExistsException 

        if password != password_repeat: 
            logger.error("Пароли не совпадают") 
            raise DontMatchPassExceptions

        hashed_password = get_password_hash(password) 

        await UsersDAO.add(session_db, user_name=user_name, password=hashed_password) 

        logger.info(f"Пользователь успешно зарегистрирован: {user_name}") 
        return {"message": "Вы успешно зарегистрированы!"}
    except Exception as e:  
        logger.error(f"Ошибка при регистрации: {str(e)}") 
        return ErrorWithRegisterException


# получение профиля пользователя
@router.get('/profile')
async def get_profile(request: Request, current_user: Users = Depends(get_current_user)):
    """
    Эндпоинт для получения профиля текущего пользователя

    Параметры:
    - request: объект запроса FastAPI
    - current_user: объект пользователя, полученный с помощью зависимости get_current_user

    Возвращает:
    - профиль пользователя, если пользователь аутентифицирован
    
    Исключения и ошибки:
    - NoUserExceptions: вызывается, если текущий пользователь не аутентифицирован
    - В случае возникновения ошибки при получении профиля, в лог записывается сообщение об ошибке, 
      и возвращается ошибка ErrorProfileException
    """
    try:
        if current_user is None:
            logger.warning('Попытка доступа к профилю без аутентификации') 
            raise NoUserExceptions

        return current_user
    
    except Exception as e: 
        logger.error(f"Ошибка при получении профиля: {str(e)}") 
        return ErrorProfileException
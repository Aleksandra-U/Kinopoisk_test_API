from fastapi import APIRouter, Depends, Request, Query, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession 
import aiohttp

from app.dao.dependencies import get_db_session
from app.movies.dao import FilmsDAO
from app.movies.dependencies import FilmsDAO, get_films_dao, get_client_session
from app.config import settings
from app.users.models import Users
from app.users.dependencies import get_current_user
from app.logger import logger
from app.exceptions import NoUserExceptions, FilmNotFoundException, NoMovieIDException, EnternalServerErrorException
from app.exceptions import NetworkErrorException, UnexpectedResponseFormatException



router = APIRouter(
    prefix="/movies/favorites",
    tags=['Любимые']
    )



#добавление фильма в избранное
@router.post("/")
async def add_to_favorites(request: Request, 
                           id: int = Query(...), 
                           current_user: Users = Depends(get_current_user),
                           films_dao_object: FilmsDAO = Depends(get_films_dao),
                           session_client: aiohttp.ClientSession = Depends(get_client_session),
                           session_db: AsyncSession = Depends(get_db_session)):
    """ 
    Эндпоинт для добавленрия фильма в избранное пользователю
 
    Параметры: 
    - request: запрос, содержащий информацию о текущем запросе
    - id: идентификатор фильма, который необходимо добавить в избранное (обязательный параметр)
    - current_user: аутентифицированный пользователь, полученный через зависимость get_current_user
    - films_dao_object: объект для доступа к данным фильмов через FilmsDAO
    - session_client: HTTP-клиент для выполнения запросов к внешним API
    - session_db: асинхронная сессия для взаимодействия с базой данных
 
    Возвращает: 
    - сообщение о результате операции (например, успешное добавление фильма в 
    избранное или информация о том, что фильм уже добавлен)
 
    Исключения: 
    - NoUserExceptions: вызывается, если текущий пользователь не аутентифицирован
    - FilmNotFoundException: если фильм с указанным идентификатором не найден
    - HTTPException: если произошла ошибка при обращении к внешнему сервису
    - NetworkErrorException: ошибка сетевого взаимодействия
    - UnexpectedResponseFormatException: если ответ от внешнего сервиса не соответствует ожидаемому формату 
    - EnternalServerErrorException: любая другая непредвиденная ошибка
    """

    if current_user is None:
        logger.warning('Попытка доступа к профилю без аутентификации') 
        raise NoUserExceptions
    
    api_key = settings.API_key
    
    url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{id}" 
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        is_exists = await films_dao_object.find_one_or_none(session_db, kinopoisk_id=id)
        if is_exists != None:
            logger.info(f'Фильм с id {id} уже присутствует в избранном пользователя {current_user.id}') 
            return {"detail": f"Фильм с id {id} уже присутствует в избранном"}
 
        async with session_client.get(url, headers=headers) as response: 
            if response.status == 404: 
                logger.error(f"Фильм с ID {id} не найден") 
                raise FilmNotFoundException
            
            if response.status != 200:  
                logger.error(f"Ошибка при получении данных: {response.status}") 
                raise HTTPException(status_code=response.status, detail="Ошибка при обращении к внешнему сервису")
            
            # Получаем данные о фильме 
            film_data = await response.json() 

            # Проверяем структуру ответа 
            if isinstance(film_data, dict) and 'kinopoiskId' in film_data: 
                film_info = film_data  
                
                # Извлекаем необходимые поля 
                kinopoisk_id = film_info.get("kinopoiskId") 
                film_name = film_info.get("nameRu", "") 
                description = film_info.get("description", "") 

                print(kinopoisk_id)
                print(film_name)
                print(description)

                await films_dao_object.add_movie_to_db(current_user.id, kinopoisk_id, film_name, description, session_db)

                return {'message': 'Film added to favorites'} 
            else:
                logger.error(f"Неожиданный формат ответа: {film_data}")  # Логируем неожиданный ответ 
                raise UnexpectedResponseFormatException
    
    except aiohttp.ClientError as e:  # Обработка сетевых ошибок 
        logger.error(f"Сетевая ошибка: {str(e)}") 
        raise NetworkErrorException
    except Exception as e:  # Обработка всех других исключений 
        print(e)
        logger.error(f"Ошибка: {str(e)}") 
        raise EnternalServerErrorException




#Удаление фильма из избранного
@router.delete("/{kinopoisk_id}")
async def delete_from_favorites(request: Request, 
                           kinopoisk_id: int, 
                           current_user: Users = Depends(get_current_user),
                           films_dao_object: FilmsDAO = Depends(get_films_dao),
                           session_db: AsyncSession = Depends(get_db_session)):
    
    """ 
    Обработчик HTTP DELETE-запроса для удаления фильма из избранного пользователя по его 
    идентификатору kinopoisk_id
 
    Параметры: 
    - request: запрос от клиента 
    - kinopoisk_id: идентификатор фильма на КиноПоиске, который необходимо удалить из избранного
    - current_user: объект пользователя, полученный из зависимости get_current_user, необходимый 
    для проверки аутентификации
    - films_dao_object: DAO-объект для работы с фильмами, полученный из зависимости get_films_dao
    - session_db: асинхронная сессия базы данных, полученная из зависимости get_db_session
 
    Возвращает: 
    - JSON-ответ с сообщением о статусе операции: 
        если фильм успешно удален - {"detail": "Фильм успешно удален из избранного"}
        если фильм не найден в избранном - {"detail": "Фильм не найден в избранном"}
     
    Исключения: 
    - NoUserExceptions: вызывается, если текущий пользователь не аутентифицирован 
    - NoMovieIDException: вызывается при возникновении неизвестной ошибки при удалении фильма
    """

    if current_user is None:
        logger.warning('Попытка доступа к профилю без аутентификации') 
        raise NoUserExceptions

    try: 
        is_exists = await films_dao_object.find_one_or_none(session_db,kinopoisk_id=kinopoisk_id)
        if is_exists is None: 
            logger.warning(f'Фильм с kinopoisk_id {kinopoisk_id} не найден в избранном пользователя {current_user.id}') 
            return {"detail": "Фильм не найден в избранном"}

        await films_dao_object.del_by_id(current_user.id, kinopoisk_id, session_db) 

        return {"detail": "Фильм успешно удален из избранного"}

    except Exception as e: 
        print(e)
        logger.error(f'Неизвестная ошибка при удалении фильма: {str(e)}') 
        raise NoMovieIDException






# просмотр списка избранных фильмов
@router.get("/")
async def get_all_information(request: Request, 
                            current_user: Users = Depends(get_current_user),
                            films_dao_object: FilmsDAO = Depends(get_films_dao),
                            session_db: AsyncSession = Depends(get_db_session)):
    
    """ 
    Эндпоинт на поучение всей информации о фильмах для текущего пользователя
 
    Параметры: 
    - request: текущий запрос от клиента
    - current_user: информация о текущем пользователе, получаемая из системы аутентификации
    - films_dao_object: объект DAO для работы с фильмами
    - session_db: объект сессии базы данных для выполнения асинхронных операций
 
    Возвращает: 
    - список фильмов, доступных для текущего пользователя
 
    Исключения и ошибки: 
    - NoUserExceptions: вызывается, если текущий пользователь не аутентифицирован

    """

    if current_user is None:
        logger.warning('Попытка доступа к профилю без аутентификации') 
        raise NoUserExceptions
    
    
    movies = await films_dao_object.get_all(current_user.id, session_db)
    return movies
      
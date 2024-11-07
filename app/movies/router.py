from fastapi import APIRouter, Depends, Request, Query
from urllib.parse import quote
import aiohttp

from app.config import settings
from app.movies.dependencies import get_client_session
from app.logger import logger
from app.exceptions import NoUserExceptions, ExternalAPIException, FilmNotFoundException, UnexpectedStructureException
from app.exceptions import UnexpectedResponseFormatException, ErrorWithResponseException, ErrorGettingDetailsException
from app.users.models import Users
from app.users.dependencies import get_current_user



router = APIRouter(
    prefix="/movies",
    tags=['Фильмы']
    )



#Поиск фильмов
@router.get("/search")
async def search_movies(request: Request, 
                        keyword: str = Query(...), 
                        current_user: Users = Depends(get_current_user),
                        session_client: aiohttp.ClientSession = Depends(get_client_session)
                        ):
    
    """ 
    Эндпоинт для поиска фильмов по ключевому слову
 
    Параметры: 
    - request: объект запроса
    - keyword: строка, по которой выполняется поиск фильмов (обязательный параметр)
    - current_user: текущий аутентифицированный пользователь (при отсутствии выбрасывается исключение)
    - session_client: объект сессии для выполнения запросов к внешнему API
 
    Возвращает: 
    - список фильмов, соответствующих ключевому слову, при успешном поиске
     
    Исключения и ошибки: 
    - NoUserExceptions: вызывается, если текущий пользователь не аутентифицирован
    - ExternalAPIException: если произошла ошибка при получении данных от внешнего API
    - FilmNotFoundException: если фильмы по ключевому слову не найдены
    - UnexpectedStructureException: если структура полученного ответа не соответствует ожиданиям
    - UnexpectedResponseFormatException: если полученный ответ имеет непредвиденный формат
    - ErrorWithResponseException: если произошла другая ошибка в процессе обработки запроса
    """

    if current_user is None:
            logger.warning('Попытка доступа к профилю без аутентификации') 
            raise NoUserExceptions
    

    api_key = settings.API_key
    
    url = f"https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={quote(keyword)}" 

    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        async with session_client.get(url, headers=headers) as response: 
            if response.status != 200: 
                logger.error(f"Ошибка при получении данных от внешнего сервиса: {response.status}") 
                raise ExternalAPIException
            
            result = await response.json()
        
            # Валидация структуры ответа 
            if isinstance(result, dict) and 'films' in result: 
                films = result['films'] 
                if isinstance(films, list): 
                    if not films:
                        logger.warning(f"Фильмы по ключевому слову '{keyword}' не найдены.") 
                        raise FilmNotFoundException 
                    return films
                else:  
                    logger.error(f"Ожидался список 'films', получен: {type(films).name}: {result}") 
                    raise UnexpectedStructureException
            else:  
                logger.error(f"Непредвиденный формат ответа: {result}")  
                raise UnexpectedResponseFormatException
    except Exception as e: 
        logger.exception("Произошла ошибка при поиске фильмов.") 
        raise ErrorWithResponseException



# получение деталей фильма
@router.get("/{id}")
async def get_ditails(request: Request, id: int, 
                      current_user: Users = Depends(get_current_user),
                      session: aiohttp.ClientSession = Depends(get_client_session)
                      ):
    
    """ 
    Эндпоинт на получение деталей фильма по его идентификатору (id)
 
    Параметры: 
    - request: объект запроса FastAPI
    - id: идентификатор фильма, передаваемый в URL
    - current_user: информация о текущем пользователе, получаемая с помощью зависимости
    - session: асинхронная сессия для выполнения HTTP-запросов к API

    Возвращает: 
    - словарь с деталями фильма, если запрос успешен и ответ имеет ожидаемую структуру
 
    Исклчения и ошибки: 
    - NoUserExceptions: вызывается, если текущий пользователь не аутентифицирован
    - FilmNotFoundException: если фильм с заданным ID не найден
    - UnexpectedResponseFormatException: если получен непредвиденный формат ответа от API 
    - ErrorGettingDetailsException: вызывается при возникновении ошибки во время получения деталей фильма
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
        async with session.get(url, headers=headers) as response: 
            if response.status != 200: 
                logger.error(f"Фильм с ID {id} не найден") 
                raise FilmNotFoundException
            
            result = await response.json()
        

            # валидация структуры ответа 
            if isinstance(result, dict) and 'kinopoiskId' in result: 
                return result 
            else: 
                logger.error(f"Непредвиденный формат ответа: {result}") 
                raise UnexpectedResponseFormatException
    except Exception as e: 
        logger.exception("Произошла ошибка при получении деталей фильма.") 
        raise ErrorGettingDetailsException
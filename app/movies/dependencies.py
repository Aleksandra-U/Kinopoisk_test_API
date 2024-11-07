import aiohttp

from app.database import async_session_maker
from app.movies.dao import FilmsDAO


async def get_films_dao(): 
    return FilmsDAO()


async def get_client_session(): 
    async with aiohttp.ClientSession() as session: 
        yield session


async def get_db_session(): 
    async with async_session_maker() as session: 
        yield session 
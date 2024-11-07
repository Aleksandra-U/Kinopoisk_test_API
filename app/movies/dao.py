from app.dao.base import BaseDAO
from app.movies.models import Films
from app.users.models import Users
from sqlalchemy.ext.asyncio import AsyncSession




class UsersDAO(BaseDAO): 
    model = Users

class FilmsDAO(BaseDAO): 
    model = Films

    @classmethod 
    async def add_movie_to_db(cls, user_id: int, kinopoisk_id: int, film_name: str, description: str, session: AsyncSession): 
        new_movie = cls.model(user_id=user_id, kinopoisk_id=kinopoisk_id, film_name=film_name, description=description) 
        session.add(new_movie) 
        await session.commit()       
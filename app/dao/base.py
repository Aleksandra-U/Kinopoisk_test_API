from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

class BaseDAO:
    model = None

    @classmethod
    async def find_by_id(cls, model_id: int, session: AsyncSession):
        query = select(cls.model).filter(cls.model.id == model_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **data):
        query = select(cls.model).filter_by(**data)
        result = await session.execute(query)
        return result.scalar_one_or_none()  
        
    @classmethod
    async def add(cls,session: AsyncSession, **data):
        query = insert(cls.model).values(**data)
        await session.execute(query)
        await session.commit()

        query = select(cls.model).filter_by(**data)
        result = await session.execute(query)
        return result.scalar()    
    
    @classmethod 
    async def del_by_id(cls, user_id: int, kinopoisk_id: int, session: AsyncSession): 
        query = delete(cls.model).where(cls.model.user_id == user_id, cls.model.kinopoisk_id == kinopoisk_id) 
        await session.execute(query) 
        await session.commit()

    @classmethod
    async def get_all(cls, user_id: int, session: AsyncSession):
            query = select(cls.model).filter(cls.model.user_id == user_id)
            result = await session.execute(query)
            return result.scalars().all()
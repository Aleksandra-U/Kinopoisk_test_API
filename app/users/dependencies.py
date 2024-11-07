from fastapi import Request, Depends
from jose import jwt, JWTError
from datetime import datetime,timezone
from app.users.dao import UsersDAO
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.dependencies import get_db_session


from app.config import settings


from app.exceptions import UserIsNotPresentException, IncorrectFormatTokenException, TokenAbsentException, TokenExpiredException

def get_token(request: Request): 
    token = request.cookies.get('booking_access_token')
    if not token:
        raise TokenAbsentException
    return token 



async def get_current_user(token: str = Depends(get_token), session: AsyncSession = Depends(get_db_session)):
    try:  
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )	
    except JWTError:
        raise IncorrectFormatTokenException
    expire: str = payload.get('exp') 
    if (not expire) or (int(expire) < datetime.now(timezone.utc).timestamp()):
        raise TokenExpiredException
    user_id: str = payload.get('sub')
    if not user_id:
        raise UserIsNotPresentException
    user = await UsersDAO.find_by_id(int(user_id),session)
    if not user:
        raise UserIsNotPresentException
    return user 

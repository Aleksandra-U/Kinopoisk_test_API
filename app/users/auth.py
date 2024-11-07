from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone

from app.config import settings
from app.users.dao import UsersDAO


# хеширование пароля и проверка при входе после регистрации 
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_password_hash(password):
    return pwd_context.hash(password)

#проверка что пароль соответствует хешированной версии 
def verify_password(plain_password, hashed_password):
    print('Verify')
    return pwd_context.verify(plain_password, hashed_password)    


#функция для создания токена
def create_access_token(data:dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=1)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, settings.ALGORITHM
    )	
    return encoded_jwt



# получаем пользователя
async def authenticate_user(session, user_name:str, password:str): 
    print(user_name, password)
    user = await UsersDAO.find_one_or_none(session, user_name=user_name)
    print(user)
    if user is None or not verify_password(password, user.password):
        return None
    print(user)
    return user
from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey

from app.users.models import Users

class Films(Base):
    __tablename__ = 'films'

    id = Column(Integer, primary_key= True, autoincrement=True) 
    user_id = Column(Integer, ForeignKey(Users.id),nullable=False) 
    kinopoisk_id = Column(Integer,nullable=False)
    film_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
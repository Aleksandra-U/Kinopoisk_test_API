from app.database import Base
from sqlalchemy import Column, Integer, String



class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key= True, nullable=False) 
    user_name = Column(String, nullable=False) 
    password = Column(String, nullable=False)
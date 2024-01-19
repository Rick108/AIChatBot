from database import Base
from sqlalchemy import Column, Integer, String


class User(Base):
    __tablename__ = "Users"
    user_name = Column(String, primary_key= True, index=True)
    password = Column(String)

from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String, index=True)
    password = Column(String)

    conversations = relationship("Conversation", back_populates="user")


class Conversation(Base):
    __tablename__ = "Conversations"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    json_data = Column(JSON, nullable=False)

    # Foreign key referencing the User model
    user_id = Column(Integer, ForeignKey("Users.user_id"))

    # Establish a back-reference to the User model
    user = relationship("User", back_populates="conversations")


from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship
from sqlalchemy import JSON, Integer, String, Text, ForeignKey, DateTime, Enum
from enum import Enum as BaseEnum
import json

class Base(DeclarativeBase):
    pass


class Role(BaseEnum):
    NONE = 0
    USER = 1
    ADMIN = 2

class User(Base):
  __tablename__ = 'users'
  id = mapped_column(Integer, primary_key=True)
  username = mapped_column(Text, nullable=True)
  user_id = mapped_column(Integer, unique=True, nullable=False) 
  role = mapped_column(Enum(Role), default=Role.USER)
  point = mapped_column(Integer, default=0)


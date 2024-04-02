from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text

from enum import Enum as BaseEnum

class Role(BaseEnum):
    NONE =0
    USER =1
    ADMIN =2


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id:Mapped[int]=mapped_column(primary_key=True)
    username:Mapped[str]=mapped_column(Text)
    chat_id:Mapped[str]=mapped_column(String(255),unique=True,nullable=True)
    role:Mapped[str]=mapped_column(Text,default=Role.USER)
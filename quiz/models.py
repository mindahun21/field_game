from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id:Mapped[int]=mapped_column(primary_key=True)
    username:Mapped[String]=mapped_column(Text)
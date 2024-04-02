from ast import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import JSON, Integer, String, Text,ForeignKey

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
    role:Mapped[str]=mapped_column(Text,default="user")

class Quiz(Base):
    __tablename__ = 'quizzes'
    id:Mapped[int]=mapped_column(primary_key=True)
    subject:Mapped[str]=mapped_column(Text)
    questions:Mapped[List["Question"]]=relationship(back_populates="quiz")
    

class Question(Base):
    id:Mapped[int]=mapped_column(primary_key=True)
    question:Mapped[str]=mapped_column(Text)
    options:Mapped[List[str]]=mapped_column(Text)
    ans_index:Mapped[int]=mapped_column(Integer)

    quiz_id= mapped_column(ForeignKey("quizzes.id"))
    quiz:Mapped[Quiz]= relationship(back_populates="questions")
    
    def __init__(self, question, options,ans_index, quiz=None):
        self.question = question
        self.options = JSON.dumps(options)
        self.ans_index = ans_index
        self.quiz = quiz

    def get_options(self):
        return JSON.loads(self.options)
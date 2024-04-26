from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship
from sqlalchemy import JSON, Integer, String, Text, ForeignKey, DateTime
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
    username = mapped_column(Text)
    chat_id = mapped_column(String(255), unique=True, nullable=True)
    user_id = mapped_column(Integer, unique=True, nullable=False)  # Store the Telegram user ID
    role = mapped_column(Text, default="user")
    quizzes = relationship("Quiz",back_populates="creator")
    poll_rank = relationship('PollRank',uselist=False, back_populates="user",cascade="all, delete-orphan")

class Quiz(Base):
    __tablename__ = 'quizzes'
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(Text,unique=True)
    subject = mapped_column(Text)
    creator_id =mapped_column(ForeignKey("users.id"))
    questions = relationship("Question", back_populates="quiz")
    creator = relationship("User", back_populates="quizzes")

class Question(Base):
    __tablename__ = 'questions'
    id = mapped_column(Integer, primary_key=True)
    question = mapped_column(Text)
    options = mapped_column(Text)
    ans_index = mapped_column(Integer)
    quiz_id = mapped_column(ForeignKey("quizzes.id"))
    quiz = relationship("Quiz", back_populates="questions")

    def __init__(self,question, options, ans_index, quiz_id):
        self.question = question
        self.options = json.dumps(options)
        self.ans_index = ans_index
        self.quiz_id = quiz_id

    def get_options(self):
        return json.loads(self.options)
    
class PollRank(Base):
    __tablename__ = 'poll_rank'
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="poll_rank")
    score = mapped_column(Integer, nullable=True)
    duration =mapped_column(Integer, nullable=True)
    end_time = mapped_column(DateTime, nullable=True)
    rank = mapped_column(Integer, nullable=True)
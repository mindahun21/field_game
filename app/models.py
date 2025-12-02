"""
This module defines the SQLAlchemy models for the application's database,
including User and Role definitions.
"""

from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship
from sqlalchemy import JSON, Integer, String, Text, ForeignKey, DateTime, Enum
from enum import Enum as BaseEnum
import json

class Base(DeclarativeBase):
    """Base class which all declarative models inherit from."""
    pass

class Role(BaseEnum):
    """Enum for defining user roles within the application."""
    NONE = 0
    USER = 1
    ADMIN = 2
    GAME_ADMIN = 3

class User(Base):
  """SQLAlchemy model for storing user information."""
  __tablename__ = 'users'
  
  id = mapped_column(Integer, primary_key=True)
  username = mapped_column(Text, nullable=True) # Telegram username
  group_name = mapped_column(Text, nullable=True, unique=True) # Unique group name for the user
  user_id = mapped_column(Integer, unique=True, nullable=False) # Telegram user ID
  role = mapped_column(Enum(Role), default=Role.USER) # User's role (e.g., USER, ADMIN, GAME_ADMIN)
  point = mapped_column(Integer, default=0) # Game points
  finished_at = mapped_column(DateTime, nullable=True) # Timestamp when the user finished the game
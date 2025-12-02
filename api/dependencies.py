"""
This module defines common dependencies for the FastAPI application,
such as database session management.
"""

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Role


# Database URL for SQLAlchemy. Configured for SQLite.
DATABASE_URL = "sqlite:///app/game.db" 

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency that provides a SQLAlchemy session for database operations.
    The session is automatically closed after the request is processed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
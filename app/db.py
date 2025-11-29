"""
This module handles the database setup and session management for the application.
It provides functions to create the SQLAlchemy engine and session,
and utilities for managing database transactions.
"""

from contextlib import contextmanager
import functools
import logging
from typing import Callable
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import dotenv_values # NEW: Import dotenv_values

# Load environment variables to get DB path
config = dotenv_values(".env")
# Database URL for SQLAlchemy. Uses SQLite and expects path from .env or defaults.
DATABASE_URL = config.get("DATABASE_URL", "sqlite:///app/game.db") 


# SQLAlchemy engine: Manages database connections.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Configures a session factory for database interactions.
localSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

logger = logging.getLogger(__name__)

def get_db() -> Session:
    """
    Provides a new SQLAlchemy session.
    """
    return localSession()

@contextmanager
def session_scope():
    """
    Provides a transactional scope around a series of database operations.
    Ensures that the session is properly committed or rolled back and closed.
    """
    session = get_db()

    try:
        logger.info("Created new database session.")
        yield session
    except SQLAlchemyError:
        session.rollback()
        logger.exception("An SQLAlchemyError occurred during database operation.")
        raise
    finally:
        session.close()
        logger.info("Closed database session.")

def access_db(util: Callable):
    """
    Decorator to automatically inject a SQLAlchemy database session into
    asynchronous utility functions.

    Args:
        util: The asynchronous function to be wrapped.

    Returns:
        The wrapped asynchronous function with database session injection.
    """
    @functools.wraps(util)
    async def inject_db(*args, **kwargs):
        with session_scope() as db:
            return await util(*args, db=db, **kwargs)
    
    return inject_db
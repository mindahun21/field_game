from contextlib import contextmanager
import functools
import logging
from typing import Callable
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

engine = create_engine('sqlite:///app/game.db')

localSession = sessionmaker(bind=engine,autoflush=False, autocommit=False, expire_on_commit=False)

logger = logging.getLogger(__name__)

def get_db() -> Session:
    return localSession()

@contextmanager
def session_scope():
    session = get_db()

    try:
        logger.info("create new session")
        yield session
    except SQLAlchemyError:
        session.rollback()
        logger.exception("An Exception has occured:")
        raise
    finally:
        session.close()
        logger.info("Closed a session")

def access_db(util:Callable):
    @functools.wraps(util)
    async def inject_db(*args,**kwargs):
        with session_scope() as db:
            return await util(*args,db=db,**kwargs)
    
    return inject_db


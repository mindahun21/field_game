"""
This module configures the application-wide logging system, setting up
different loggers for general application messages, SQLAlchemy, and
directing logs to various files based on severity.
"""

import logging

def init_logger():
    """
    Initializes and configures the application's logging system.
    Sets up 'app' logger for general messages (WARNING to app.log, INFO to info.log)
    and 'sqlalchemy' logger for database-related messages (INFO to db.log).
    """
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)

    main_handler =logging.FileHandler("app.log",mode="a")
    main_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    main_handler.setFormatter(formatter)

    secondary_handler= logging.FileHandler("info.log",mode="a")
    secondary_handler.setLevel(logging.INFO)
    secondary_handler.setFormatter(formatter)

    logger.addHandler(main_handler)
    logger.addHandler(secondary_handler)

    sqlalchemy_logger = logging.getLogger("sqlalchemy")
    sqlalchemy_logger.setLevel(logging.INFO)

    sqlalchemy_handler = logging.FileHandler("db.log", mode="a")
    sqlalchemy_handler.setFormatter(formatter)

    sqlalchemy_logger.addHandler(sqlalchemy_handler)
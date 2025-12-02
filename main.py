"""
This module serves as the main entry point for the Telegram bot application.
It initializes the logger, database, loads environment variables,
builds the Telegram `Application` instance, and registers all bot handlers.
When run directly, it confirms bot initialization for webhook operation.
"""

# Removed: from dotenv import dotenv_values
import logging

from app.logger import init_logger
from app.db import engine
from app.models import Base
from app.handlers import get_handlers, register_handler
from app.errors import error_handler
import field_game

from common.callback_handler import handle_callback

from telegram.ext import ApplicationBuilder, CallbackQueryHandler

from telegram import Update
from dotenv import dotenv_values

config = dotenv_values(".env")

# from app.config import config # NEW: Import config from app.config


# Initialize logger first to ensure it's ready for subsequent logging calls
init_logger() 
logger = logging.getLogger(__name__) # Get logger instance

# Database setup before application build
Base.metadata.create_all(bind=engine) 

# Load environment variables (now from app.config)
# Removed: config = dotenv_values(".env")
API_KEY = config["API_KEY"]


application =(
    ApplicationBuilder()
    .token(API_KEY)
    .concurrent_updates(True)
    .build()
)

application.add_handlers(get_handlers())
application.add_error_handler(error_handler)
application.add_handler(CallbackQueryHandler(handle_callback))


if __name__ == '__main__':
    logger.info("Bot application configured. Designed for webhook operation via FastAPI.")
    # In webhook mode, the bot's logic runs within the FastAPI server once it starts.
    # No direct polling or uvicorn.run from this script.


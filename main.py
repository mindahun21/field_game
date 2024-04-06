from dotenv import dotenv_values

from app.logger import init_logger
from app.db import engine
from app.models import Base
from app.handlers import get_handlers
from app.errors import error_handler

from common.callback_handler import handle_callback

from telegram.ext import ApplicationBuilder, CallbackQueryHandler

from telegram import Update



if __name__ == '__main__':

    init_logger()
    Base.metadata.create_all(bind=engine)
    config=dotenv_values(".env")
    API_KEY = config["API_KEY"]
    print("BOT started.")
    application =(
        ApplicationBuilder()
        .token(API_KEY)
        .concurrent_updates(True)
        .build()
    )

    print(get_handlers())

    application.add_handlers(get_handlers())
    application.add_error_handler(error_handler)
    application.add_handler(CallbackQueryHandler(handle_callback))

    application.run_polling(allowed_updates=Update.ALL_TYPES, timeout=20)

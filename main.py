from dotenv import dotenv_values

from app.logger import init_logger
from app.db import engine
from app.models import Base
from app.handlers import get_handlers, register_handler
from app.errors import error_handler

from quiz.add_question import handler as add_question_handler
from quiz.create_quiz import handler as create_handler_handler
from quiz.take_quiz import handler as take_quiz_handler

from common.callback_handler import handle_callback

from telegram.ext import ApplicationBuilder, CallbackQueryHandler

from telegram import Update



if __name__ == '__main__':

    init_logger()
    Base.metadata.create_all(bind=engine)
    config=dotenv_values(".env")
    API_KEY = config["API_KEY"]
    print("BOT started.")

    register_handler(add_question_handler)
    register_handler(create_handler_handler)
    register_handler(take_quiz_handler)

    application =(
        ApplicationBuilder()
        .token(API_KEY)
        .concurrent_updates(True)
        .build()
    )

    # print(get_handlers())

    application.add_handlers(get_handlers())
    application.add_error_handler(error_handler)
    application.add_handler(CallbackQueryHandler(handle_callback))

    application.run_polling(allowed_updates=Update.ALL_TYPES, timeout=20)

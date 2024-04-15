import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import Forbidden

from .db import session_scope
from .db_utils import get_entries
from .models import User



logger= logging.getLogger(__name__)

async def error_handler(update:Update,context: ContextTypes.DEFAULT_TYPE):
    if isinstance(context.error ,Forbidden):
        chat_id = update.effective_chat.id if update.effective_chat else None
        if chat_id:
            await context.bot.send_message(chat_id, "Sorry, for sad news \n the user has blocked the bot")        
            return
    
    logger.error("An exception has occurred", exc_info=context.error)
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id:
        await context.bot.send_message(
            chat_id,
            "We are extremely sorry but an error occurred on our side. Please redo your recent action.\n\nWe are working on fixing this issue.",
        )

    with session_scope() as db:
        admins = await get_entries(User,db=db,role="admin")

        if not admins:
            return
        
        for admin in admins:
            await context.bot.send_message(
                admin.chat_id,
                f"An error occured in the bot. Please check the logs for more info.\n\nError: <pre>{context.error}</pre>",
                parse_mode="HTML"
            )


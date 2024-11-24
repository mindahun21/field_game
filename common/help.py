from app.db import access_db
from app.db_utils import get_role
from app.models import Role
from app.handlers import register_handler
from app.utils import callback_handler

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


@access_db
async def help_handler(update:Update, context=ContextTypes.DEFAULT_TYPE, db=None):

    role,_ =await get_role(user_id=update.effective_user.id, db=db)

    msg =None

    if role == Role.USER:
        msg="USER COMMANDS:\nuse /take_quiz command to take quiz.\n "
    elif role == Role.ADMIN:
        msg="ADMIN COMMANDS:\nuse /create_quiz to create quiz.\n"
        msg+="Use /take_quiz command to take quiz.\n"
    else:
        msg="please first start the bot by using /start command"

    if msg:
        await update.message.reply_text(msg)

# handler = CommandHandler("help",help_handler)
# register_handler(handler)


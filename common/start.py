from sqlalchemy.orm import Session

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from app import db_utils
from app.db import access_db
from app.models import Role,User
from app.handlers import register_handler

admins =[
    {
        "username": "Mindahun21",
    }
]

async def is_admin(username):
    for user in admins:
        if user["username"] == username:
            return user
    
    return False


@access_db
async def start(update:Update, context:ContextTypes.DEFAULT_TYPE,db:Session=None):
    role, _ = await db_utils.get_role(update.effective_chat.id,db=db)
    if role == Role.USER:        
        await update.message.reply_text(
            f"hello {update.effective_chat.username}:\nuse /help comand to start using the bot"
        )
    elif role == Role.ADMIN:
        await update.message.reply_text(
            f"hello, ADMIN {update.effective_chat.username}:\nuse /help to start using this bot as admin"
        )
    elif admin:= await is_admin(update.message.from_user.username):
        user = User(
            username=admin["username"],
            chat_id=update.effective_chat.id,
            role="admin",
        )
        await db_utils.add_obj(user,db=db)
        await update.message.reply_text(
            f"hello, ADMIN {update.effective_chat.username}:\nuse /help to start using this bot as admin"
        )
    elif role == Role.NONE:
        user = User(
            username=update.message.from_user.username,
            chat_id=update.effective_chat.id,
            role="user",
        )

        await db_utils.add_obj(user,db=db)
        await update.message.reply_text(
            f"hello {update.effective_chat.username}:\nuse /help comand to start using the bot"
        )


handler = CommandHandler("start",start)
register_handler(handler)

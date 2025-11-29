"""
This module defines the help command handler for the bot,
providing users with a list of available commands based on their role.
"""

from app.db import access_db
from app.db_utils import get_role
from app.models import Role
from app.handlers import register_handler
from app.utils import callback_handler

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


@access_db
async def help_handler(update:Update, context=ContextTypes.DEFAULT_TYPE, db=None):
    """
    Handles the /help command, sending a list of available commands
    to the user based on their role (USER, GAME_ADMIN, ADMIN, or NONE).
    """
    role,_ =await get_role(user_id=update.effective_user.id, db=db)

    msg = None

    if role == Role.USER:
        msg = "USER COMMANDS:\n"
        msg += "  - /start: Start the game.\n"
        msg += "  - /help: Show available commands.\n"
    elif role == Role.GAME_ADMIN:
        msg = "GAME ADMIN COMMANDS:\n"
        msg += "  - /start: Start the game.\n"
        msg += "  - /help: Show available commands.\n"
        msg += "  - /update_point: Open the mini-app to update user points.\n"
    elif role == Role.ADMIN:
        msg = "SUPER ADMIN COMMANDS:\n"
        msg += "  - /start: Start the game.\n"
        msg += "  - /help: Show available commands.\n"
        msg += "  - /reset: Reset the game (deletes all user data).\n"
        msg += "  - /result: Get the ranked list of finishers.\n"
        msg += "  - /update_point: Open the mini-app to update user points.\n"
        msg += "  - /transfer_group: Transfer group ownership to another user.\n"
    else: # Role.NONE
        msg = "Please first start the bot by using /start command."

    if msg:
        await update.message.reply_text(msg)

# Command handler for the /help command.
handler = CommandHandler("help",help_handler)
register_handler(handler)
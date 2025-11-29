"""
This module contains the core game logic, Telegram bot command handlers,
and the conversation flow for the Field Game bot. It manages user interactions,
game states, and administrative commands.
"""

from enum import Enum
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

from dotenv import dotenv_values



from .data import *
from .utils import *

from telegram.ext import(
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from telegram import(
    Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, BotCommand, BotCommandScopeChat
)

from app import db_utils
from app.db import access_db
from app.models import Role,User
from app.handlers import register_handler
from app.utils import cancel_conversation,invalid_message

config = dotenv_values(".env")


class State(Enum):
    """
    Enum representing the different states in the game conversation flow.
    """
    DISTRIBUTER=0
    FIRST_GAME=1
    GET_GROUP_NAME=2
    
game = Game()
logger = logging.getLogger(__name__)


ROLE_COMMANDS = {
    Role.NONE: [
        BotCommand("start", "Start the bot / Register"),
        BotCommand("help", "Show available commands"),
    ],
    Role.USER: [
        BotCommand("start", "Restart the game / Check status"),
        BotCommand("help", "Show available commands"),
        BotCommand("cancel", "Cancel current operation"),
    ],
    Role.GAME_ADMIN: [
        BotCommand("start", "Restart the game / Check status"),
        BotCommand("help", "Show available commands"),
        BotCommand("update_point", "Open app to update points"),
    ],
    Role.ADMIN: [
        BotCommand("start", "Restart the game / Check status"),
        BotCommand("help", "Show available commands"),
        BotCommand("update_point", "Open app to update points"),
        BotCommand("result", "Get ranked list of finishers"),
        BotCommand("reset", "Reset the game (DANGER)"),
        BotCommand("transfer_group", "Transfer group ownership"),
    ],
}

async def set_role_based_commands(user_id: int, role: Role, context: ContextTypes.DEFAULT_TYPE):
    """
    Dynamically sets the list of commands visible to a user in Telegram's chat input
    based on their assigned role.

    Args:
        user_id: The Telegram user ID for whom to set commands.
        role: The Role enum of the user.
        context: The ContextTypes.DEFAULT_TYPE object for bot interactions.
    """
    commands_for_role = ROLE_COMMANDS.get(role, ROLE_COMMANDS[Role.NONE])
    try:
        await context.bot.set_my_commands(commands_for_role, scope=BotCommandScopeChat(chat_id=user_id))
        logger.info(f"Set commands for user {user_id} (Role: {role.name}) to: {[cmd.command for cmd in commands_for_role]}")
    except Exception as e:
        logger.error(f"Failed to set commands for user {user_id} (Role: {role.name}): {e}")


@access_db
async def start_game(update:Update,context:ContextTypes.DEFAULT_TYPE,db:Session=None):
    """
    Handles the /start command.
    Initiates a new game conversation or provides status for existing users.
    Sets role-based commands for the user.
    """
    user_id = update.effective_user.id
    user = await db_utils.get_entry(User, db=db, user_id=user_id)

    if user:
        if user.role == Role.ADMIN:
            await context.bot.send_message(
                user_id,
                f"<pre>hello, {update.effective_user.username}:\nyou are a Super Admin. You have access to all commands: /reset, /result, /update_point.</pre>",
                parse_mode="HTML"
            )
            await set_role_based_commands(user_id, user.role, context)
            return ConversationHandler.END
        elif user.role == Role.GAME_ADMIN:
            await context.bot.send_message(
                user_id,
                f"<pre>hello, {update.effective_user.username}:\nyou are a Game Admin. You can use /update_point to manage game points.</pre>",
                parse_mode="HTML"
            )
            await set_role_based_commands(user_id, user.role, context)
            return ConversationHandler.END
        elif user.group_name:
            await update.message.reply_text(
                f"You are already in the game with group '{user.group_name}'. Continue playing!"
            )
            await set_role_based_commands(user_id, user.role, context)
            return State.DISTRIBUTER
        else:
            await update.message.reply_text("Welcome back! Please enter your unique group name to continue.")
            await set_role_based_commands(user_id, user.role, context)
            return State.GET_GROUP_NAME
          
    elif admin:= await game.is_admin(update.effective_user.username):
        user = User(
            username=admin["username"],
            user_id=update.effective_user.id,
            role=Role.ADMIN
        )
        await db_utils.add_obj(user,db=db)
        await context.bot.send_message(
            update.effective_user.id,
            f"<pre>hello, {update.effective_user.username}:\nyou are a Super Admin. You have access to all commands: /reset, /result, /update_point.</pre>",
            parse_mode="HTML"
        )
        await set_role_based_commands(user_id, user.role, context)
        return
    else:
        new_role = Role.USER
        for game_admin in game.game_admins:
            if update.effective_user.username == game_admin["username"]:
                new_role = Role.GAME_ADMIN
                break
        
        user = User(
            username=update.effective_user.username,
            user_id=update.effective_user.id,
            role=new_role
        )
        await db_utils.add_obj(user, db=db)
        
        if new_role == Role.GAME_ADMIN:
            await context.bot.send_message(
                user_id,
                f"<pre>hello, {update.effective_user.username}:\nyou are a Game Admin. You can use /update_point to manage game points.</pre>",
                parse_mode="HTML"
            )
            await set_role_based_commands(user_id, user.role, context)
            return ConversationHandler.END
        else:
            await update.message.reply_text("Welcome! Please enter a unique group name.\n\n"
                                            "Group names can contain letters, numbers, and common symbols, "
                                            "but emojis are not allowed.")
            await set_role_based_commands(user_id, new_role, context)
            return State.GET_GROUP_NAME


@access_db
async def get_group_name(update:Update, context:ContextTypes.DEFAULT_TYPE, db:Session=None):
    """
    Handles the GET_GROUP_NAME state, where a new user provides their group name.
    Registers the user with the provided group name and sets their commands.
    """
    user_id = update.effective_user.id
    group_name = update.message.text
    
    # Validate group_name format
    import re
    if not re.match(r'^[\w\s\d\u1200-\u137F\u1390-\u139F\u0020-\u007E]+$', group_name):
        await update.message.reply_text(
            "Invalid group name. Please use only letters, numbers, and common symbols. Emojis are not allowed."
        )
        return State.GET_GROUP_NAME

    if await db_utils.is_group_name_taken(group_name, db=db):
        await update.message.reply_text("That group name is already taken. Please choose another one.")
        return State.GET_GROUP_NAME

    user = await db_utils.get_entry(User, db=db, user_id=user_id)
    if not user:
        logger.error(f"User {user_id} not found in get_group_name, but expected to exist.")
        await update.message.reply_text("An unexpected error occurred. Please try /start again.")
        return ConversationHandler.END

    await db_utils.set_val(user, db=db, group_name=group_name)
    
    await update.message.reply_text(
        f"Thank you, {group_name}! Your group has been registered.\n\n{game.ruls}"
    )
    await update.message.reply_text(
      "የመጀመሪያው ጨዋታ ይህንን (MAZE) በትክክል መጨረስ እና ያገኛችሁትን ሐረግ ለአቻዋቾች ማሳየት ነው  \n👇👇👇👇👇"
    )
    await send_photo(context, user_id, "images/maze_game1.jpg")
    await set_role_based_commands(update.effective_user.id, Role.USER, context)
    return State.DISTRIBUTER


@access_db
async def distributer(update:Update,context:ContextTypes.DEFAULT_TYPE, db:Session=None):
  """
  Handles the main game distribution state, processing user codes.
  """
  if update.message is not None:  
      code = update.message.text

  status = game.check_code(code)
  user = await db_utils.get_entry(User, db=db,user_id = update.effective_user.id)

  if status == 404:
    await update.message.reply_text(game.wrong_msg)
    return State.DISTRIBUTER
  

  if status == 200:
    user.finished_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)
    await context.bot.send_message(
      update.effective_user.id,
      "congradulations👏 your team finished the game",
      parse_mode="HTML"
    )
    return ConversationHandler.END

  elif status in range(2,6):
    question = game.games.get(str(status),False)
    await update.message.reply_text(f"{question}")

    puzzle = game.redirect_puzzle.get(str(status),False)
    await update.message.reply_text(f"{puzzle}")

  return State.DISTRIBUTER


@access_db
async def reset_game(update: Update, context: ContextTypes.DEFAULT_TYPE, db:Session =None):
  """
  Resets the entire game, deleting all user data and re-registering the
  commanding admin. This is an ADMIN-only command.
  """
  user_id = update.effective_user.id
  role, _ = await db_utils.get_role(user_id,db=db)
  
  if role != Role.ADMIN:
    await update.message.reply_text(
       "You are not authorized to use this command."
    )
    return
     
  # Delete all users and game state
  await db_utils.delete_all_rows(User, db=db)
  
  # Re-register the admin who initiated the reset
  user = User(
    username=update.effective_user.username,
    user_id=user_id,
    role=Role.ADMIN
  )
  await db_utils.add_obj(user,db=db)
    
  game.reset() # Reset game data in memory

  await context.bot.send_message(
     user_id,
     text=f"The game is successfully reseted."
  )
  await set_role_based_commands(user_id, Role.ADMIN, context)


@access_db
async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE, db:Session =None):
  """
  Generates and sends a ranked list of finishers to all finishers and admins.
  This is an ADMIN-only command.
  """
  role, _ = await db_utils.get_role(update.effective_user.id,db=db)
  if role != Role.ADMIN:
    await update.message.reply_text(
       "You can't use this command because you are not an admin."
    )
    return
  
  finished_users = db.query(User).filter(User.finished_at.isnot(None)).order_by(User.finished_at).all()
  admin_message = "The Winners are:\n<pre>"
  
  for index, user in enumerate(finished_users):
    admin_message += f"{index+1}. {user.group_name} (@{user.username or 'no username'}) points: {user.point}\n"

  admin_message += "</pre>"
  
  admins = await db_utils.get_entries(User, db=db, role=Role.ADMIN)
  
  recipient_ids = set([user.user_id for user in finished_users])
  for admin in admins:
      recipient_ids.add(admin.user_id)

  for user_id in recipient_ids:
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=admin_message,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send message to {user_id}: {e}")

@access_db
async def update_point_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Session = None):
  """
  Provides ADMINs and GAME_ADMINs with a link to the mini-app for updating user points.
  """
  user_id = update.effective_user.id
  role, _ = await db_utils.get_role(user_id, db=db)
  logger.info(f"User {user_id} with role {role} invoked /update_point command.")

  if role == Role.ADMIN or role == Role.GAME_ADMIN:
      role_str = role.name 
      mini_app_base_url = config["MINI_APP_BASE_URL"]
      mini_app_url = f"{mini_app_base_url}/?role={role_str}"

      keyboard = [
          [InlineKeyboardButton("Open Mini-App", web_app=WebAppInfo(url=mini_app_url))]
      ]
      reply_markup = InlineKeyboardMarkup(keyboard)
      await update.message.reply_text(
          "Click the button below to open the points update mini-app:",
          reply_markup=reply_markup
      )
  else:
      await update.message.reply_text(
          "You are not authorized to use this command."
      )

@access_db
async def transfer_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Session = None):
    """
    Provides ADMINs with a link to the mini-app for transferring group ownership.
    This is an ADMIN-only command.
    """
    user_id = update.effective_user.id
    role, _ = await db_utils.get_role(user_id, db=db)

    if role == Role.ADMIN:
        role_str = role.name 
        mini_app_base_url = config["MINI_APP_BASE_URL"]
        mini_app_url = f"{mini_app_base_url}/?role={role_str}&view=transferOwnership"

        keyboard = [
            [InlineKeyboardButton("Open Transfer Ownership App", web_app=WebAppInfo(url=mini_app_url))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Click the button below to open the group ownership transfer app:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "You are not authorized to use this command."
        )
   
handler = ConversationHandler(
    entry_points=[CommandHandler("start",start_game)],
    states={
        State.GET_GROUP_NAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_group_name)],
        State.DISTRIBUTER:[MessageHandler(filters.TEXT & (~filters.COMMAND),distributer)],
    },
    fallbacks=[
        CommandHandler("cancel",cancel_conversation),
        MessageHandler(filters.ALL,invalid_message),
    ],
)


handler1  = CommandHandler("result",show_result)
handler2 = CommandHandler("reset",reset_game)
handler3 = CommandHandler("update_point", update_point_command)
handler4 = CommandHandler("transfer_group", transfer_group_command)
register_handler(handler1)
register_handler(handler2)
register_handler(handler3)
register_handler(handler4)
register_handler(handler)
from enum import Enum
from sqlalchemy.orm import Session
from datetime import datetime
import logging


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

class State(Enum):
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
        
        # Add other user commands here
    ],
    Role.GAME_ADMIN: [
        BotCommand("start", "Restart the game / Check status"),
        BotCommand("help", "Show available commands"),
        BotCommand("update_point", "Open app to update points"),
        # Add other game admin commands here
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
    commands_for_role = ROLE_COMMANDS.get(role, ROLE_COMMANDS[Role.NONE])
    try:
        await context.bot.set_my_commands(commands_for_role, scope=BotCommandScopeChat(chat_id=user_id))
        logger.info(f"Set commands for user {user_id} (Role: {role.name}) to: {[cmd.command for cmd in commands_for_role]}")
    except Exception as e:
        logger.error(f"Failed to set commands for user {user_id} (Role: {role.name}): {e}")


@access_db
async def start_game(update:Update,context:ContextTypes.DEFAULT_TYPE,db:Session=None):
    user_id = update.effective_user.id
    user = await db_utils.get_entry(User, db=db, user_id=user_id)

    if user:
        if user.role == Role.ADMIN:
            await context.bot.send_message(
                user_id,
                f"<pre>hello, {update.effective_user.username}:\nyou are a Super Admin. You have access to all commands: /reset, /result, /update_point.</pre>",
                parse_mode="HTML"
            )
            await set_role_based_commands(user_id, user.role, context) # Set commands
            # End conversation, as admin might want to start fresh or use other commands
            return ConversationHandler.END
        elif user.role == Role.GAME_ADMIN:
            await context.bot.send_message(
                user_id,
                f"<pre>hello, {update.effective_user.username}:\nyou are a Game Admin. You can use /update_point to manage game points.</pre>",
                parse_mode="HTML"
            )
            await set_role_based_commands(user_id, user.role, context) # Set commands
            # End conversation
            return ConversationHandler.END
        elif user.group_name: # User is registered and has a group
            await update.message.reply_text(
                f"You are already in the game with group '{user.group_name}'. Continue playing!"
            )
            await set_role_based_commands(user_id, user.role, context) # Set commands
            # Redirect to DISTRIBUTER state if they are already in game
            return State.DISTRIBUTER
        else: # User is registered but doesn't have a group yet (e.g., in GET_GROUP_NAME state)
            await update.message.reply_text("Welcome back! Please enter your unique group name to continue.")
            await set_role_based_commands(user_id, user.role, context) # Set commands
            return State.GET_GROUP_NAME
          
    elif admin:= await game.is_admin(update.effective_user.username):
        user = User(
            username=admin["username"],
            user_id=update.effective_user.id,
            role=Role.ADMIN # Still create as ADMIN
        )
        await db_utils.add_obj(user,db=db)
        await context.bot.send_message(
            update.effective_user.id,
            f"<pre>hello, {update.effective_user.username}:\nyou are a Super Admin. You have access to all commands: /reset, /result, /update_point.</pre>",
            parse_mode="HTML"
        )
        await set_role_based_commands(user_id, user.role, context) # Set commands
        return
    else:
        # New user
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
            await set_role_based_commands(user_id, user.role, context) # Set commands
            return ConversationHandler.END
        else:
            await update.message.reply_text("Welcome! Please enter a unique group name.")
            await set_role_based_commands(user_id, new_role, context) # Set commands
            return State.GET_GROUP_NAME


@access_db
async def get_group_name(update:Update, context:ContextTypes.DEFAULT_TYPE, db:Session=None):
    group_name = update.message.text
    
    # Check if group name is unique
    if await db_utils.is_group_name_taken(group_name, db=db):
        await update.message.reply_text("That group name is already taken. Please choose another one.")
        return State.GET_GROUP_NAME

    # Retrieve existing user and update their group_name
    user = await db_utils.get_entry(User, db=db, user_id=update.effective_user.id)
    if not user:
        logger.error(f"User {update.effective_user.id} not found in get_group_name, but expected to exist.")
        await update.message.reply_text("An unexpected error occurred. Please try /start again.")
        return ConversationHandler.END

    await db_utils.set_val(user, db=db, group_name=group_name)
    
    await update.message.reply_text(
        f"Thank you, {group_name}! Your group has been registered.\n\n{game.ruls}"
    )
    await update.message.reply_text(
      "የመጀመሪያው ጨዋታ አጫዋቾቻችሁ የሚሰጧችሁን (cross word puzzle) በትክክል መጨረስ ነው"
    )
    await set_role_based_commands(update.effective_user.id, Role.USER, context) # Set commands after registration
    return State.DISTRIBUTER


@access_db
async def distributer(update:Update,context:ContextTypes.DEFAULT_TYPE, db:Session=None):
  if update.message is not None:  
      code = update.message.text

  status = game.check_code(code)
  user = await db_utils.get_entry(User, db=db,user_id = update.effective_user.id)

  if status == 404:
    await update.message.reply_text(game.wrong_msg)
    return State.DISTRIBUTER
  

  if status == 200:
    user.finished_at = datetime.utcnow()
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

    if status == 5:
      await send_game5(context=context,user_id=update.effective_user.id)
    puzzle = game.redirect_puzzle.get(str(status),False)
    await update.message.reply_text(f"{puzzle}")

  return State.DISTRIBUTER


@access_db
async def reset_game(update: Update, context: ContextTypes.DEFAULT_TYPE, db:Session =None):
  role, _ = await db_utils.get_role(update.effective_user.id,db=db)
  
  if role != Role.ADMIN: # Only ADMIN can reset
    await update.message.reply_text(
       "You are not authorized to use this command."
    )
    return
     

  await db_utils.delete_all_rows(User, db=db)
  user = User(
    username=update.effective_user.username,
    user_id=update.effective_user.id,
    role=Role.ADMIN
  )
  await db_utils.add_obj(user,db=db)
    
  game.reset()

  await context.bot.send_message(
     update.effective_user.id,
     text=f"the game is successfully reseted"
  )

@access_db
async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE, db:Session =None):
  role, _ = await db_utils.get_role(update.effective_user.id,db=db)
  if role != Role.ADMIN:
    await update.message.reply_text(
       "you can't use this command b/c you are not an admin"
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
  
    user_id = update.effective_user.id
    role, _ = await db_utils.get_role(user_id, db=db)
    logger.info(f"User {user_id} with role {role} invoked /update_point command.")

    if role == Role.ADMIN or role == Role.GAME_ADMIN:
        # Convert Role enum to string for URL parameter
        role_str = role.name 
        # Placeholder for ngrok URL, user will replace this with their actual ngrok URL
        mini_app_base_url = "https://cf4900f81e5d.ngrok-free.app" # Using the user's provided ngrok URL
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
    user_id = update.effective_user.id
    role, _ = await db_utils.get_role(user_id, db=db)

    if role == Role.ADMIN: # Only ADMINs can transfer group ownership
        # Convert Role enum to string for URL parameter
        role_str = role.name 
        # Placeholder for ngrok URL, user will replace this with their actual ngrok URL
        mini_app_base_url = "https://cf4900f81e5d.ngrok-free.app" # Using the user's provided ngrok URL
        mini_app_url = f"{mini_app_base_url}/?role={role_str}&view=transferOwnership" # Pass view parameter

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
handler3 = CommandHandler("update_point", update_point_command) # New handler for update_point
handler4 = CommandHandler("transfer_group", transfer_group_command) # New handler for transfer_group
register_handler(handler1)
register_handler(handler2)
register_handler(handler3) # Register the new handler
register_handler(handler4) # Register the new handler
register_handler(handler)


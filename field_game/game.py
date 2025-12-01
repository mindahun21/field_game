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
    UPDATE_POINT_FORCE=3
    GAME22=4

game = Game()
logger = logging.getLogger("app")


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
        BotCommand("all_users_status", "Show all users' status"),
        BotCommand("all_finishers_status", "Show all finishers' status"),
        BotCommand("update_point_force", "Force update group points for a game"),
        BotCommand("current_awarded_points", "Check current awarded points for a group and game"),
        BotCommand("current_awarded_points_all", "Check current awarded points for all groups and games"),
        BotCommand("current_awarded_points_grouped", "Check current awarded points grouped by groups"),
        BotCommand("add_game_admin", "Add game admins"),
        BotCommand("remove_game_admin", "Remove game admins"),
        BotCommand("list_game_admins", "List all game admins"),
        
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
                "Admin check complete. You are already registered.",
                parse_mode="HTML"
            )
            await set_role_based_commands(user_id, user.role, context)
            return ConversationHandler.END
        elif user.role == Role.GAME_ADMIN:
            await context.bot.send_message(
                user_id,
                "Game Admin check complete. You are already registered.",
                parse_mode="HTML"
            )
            await set_role_based_commands(user_id, user.role, context)
            return ConversationHandler.END
        elif user.group_name:
            await context.bot.send_message(
                user_id,
                f"You are already in the game with group '{user.group_name}'. Continue playing!"
            )
            await set_role_based_commands(user_id, user.role, context)
            return State.DISTRIBUTER
        else:
            await context.bot.send_message(user_id, "Welcome back! Please enter your unique group name to continue.")
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
            f"""<pre>hello, {update.effective_user.username}: you are a Super Admin. You have access to all commands: /reset, /result, /update_point.</pre>""",
            parse_mode="HTML"
        )
        await set_role_based_commands(user_id, user.role, context)
        return ConversationHandler.END
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
                f"<pre>hello, {update.effective_user.username}: you are a Game Admin. You can use /update_point to manage game points.</pre>",
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
    # await update.message.reply_text(
    #   "የመጀመሪያው ጨዋታ ይህንን (MAZE) በትክክል መጨረስ እና ያገኛችሁትን ሐረግ ለአቻዋቾች ማሳየት ነው  \n👇👇👇👇👇"
    # )
    # await send_photo(context, user_id, "images/maze_game1.jpg")
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

  #TODO: send game5 using game52 codes
  elif status in range(1,7):
    if status == 1:
      await update.message.reply_text(
        "የመጀመሪያው ጨዋታ ይህንን (MAZE) በትክክል መጨረስ እና ያገኛችሁትን ቃል በትክክል (በ አማርኛ) ወደ bot መላክ  \n👇👇👇👇👇"
      )
      await send_photo(context, update.effective_user.id, "images/maze_game1.jpg")
      return State.GAME22
    
    if status != 5:
      question = game.games.get(str(status),False)
      await context.bot.send_message(update.effective_user.id, f"{question}")
    if status != 6:
      puzzle = game.redirect_puzzle.get(str(status),False)
      await context.bot.send_message(update.effective_user.id, f"{puzzle}")

  return State.DISTRIBUTER

@access_db
async def game22(update:Update,context:ContextTypes.DEFAULT_TYPE, db:Session=None):
    """
    Handles the GAME22 state, where users submit answers for Game 2.2.
    Validates the answer and provides feedback.
    """
    answer = update.message.text.strip()
    correct_answer = "ሐዋርያት"

    if answer == correct_answer:
        await context.bot.send_message(
            update.effective_user.id,
            game.game2
        )
        return State.DISTRIBUTER
    else:
        await update.message.reply_text(
            "Incorrect answer. Please try again. Remember to write the answer in Amharic."
        )
        return State.GAME22

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
  game.add_awarded_points = {}

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
  logger.info(f"User {update.effective_user.id} invoked /result command.")
  role, _ = await db_utils.get_role(update.effective_user.id,db=db)
  if role != Role.ADMIN:
    await update.message.reply_text(
       "You can't use this command because you are not an admin."
    )
    return
  
  #TODO: give priority for points
  finished_users = db.query(User).filter(User.finished_at.isnot(None)).order_by(User.point.desc(), User.finished_at.asc()).all()
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
        
@access_db
async def all_users_status(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Session = None):
    """
    ADMIN command to list all users with their group names and points.
    """
    user_id = update.effective_user.id
    role, _ = await db_utils.get_role(user_id, db=db)

    if role != Role.ADMIN:
        await update.message.reply_text(
            "You are not authorized to use this command."
        )
        return

    users = await db_utils.get_entries(User, db=db)
    users = sorted(users, key=lambda u: u.point or 0, reverse=True)
    message = "All Users Status:\n<pre>"
    for i, user in enumerate(users):
        message += f"No: {i+1}, User: @{user.username or 'no username'}, Role: {user.role.name if user.role else 'no role'}, Group: {user.group_name or 'no group'}, Points: {user.point}\n"
    message += "</pre>"

    await update.message.reply_text(
        message,
        parse_mode="HTML"
    )
    
@access_db
async def all_finishers_status(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Session = None):
    """
    ADMIN command to list all finishers with their group names and points.
    """
    user_id = update.effective_user.id
    role, _ = await db_utils.get_role(user_id, db=db)

    if role != Role.ADMIN:
        await update.message.reply_text(
            "You are not authorized to use this command."
        )
        return

    finishers = await db_utils.get_entries(User, db=db)
    finishers = [user for user in finishers if user.finished_at is not None]
    finishers = sorted(finishers, key=lambda u: u.point or 0, reverse=True)
    message = "All Finishers Status:\n<pre>"
    for i, user in enumerate(finishers):
        message += f"No: {i+1}, User: @{user.username or 'no username'}, Group: {user.group_name or 'no group'}, Points: {user.point}\n"
    message += "</pre>"

    await update.message.reply_text(
        message,
        parse_mode="HTML"
    )
    
@access_db
async def update_group_point_for_game_even_if_already_awarded(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Session = None):
    """
    ADMIN command to forcibly update a group's points for a specific game,
    even if points have already been awarded for that game.
    """
    user_id = update.effective_user.id
    role, _ = await db_utils.get_role(user_id, db=db)

    if role != Role.ADMIN:
        await update.message.reply_text(
            "You are not authorized to use this command."
        )
        return

    try:
        parts = update.message.text.split()
        if len(parts) != 4:
            raise ValueError("Incorrect number of arguments.")

        _, group_name, game_number_str, points_str = parts
        points = int(points_str)
        game_number = int(game_number_str)
    except Exception as e:
        await update.message.reply_text(
            "Usage: /update_point_force <group_name> <game_number> <points>\n"
            "Example: /update_point_force TeamA 2 10"
        )
        return

    user = await db_utils.get_entry(User, db=db, group_name=group_name)
    if not user:
        await update.message.reply_text(
            f"No group found with name '{group_name}'."
        )
        return
      
    current_points = game.get_awarded_points(group_name, game_number)

    user.point = (user.point or 0) + points - current_points
    await db_utils.add_obj(user, db=db)

    # Update the awarded points tracking
    game.add_awarded_points(group_name, game_number, points)
    total_points_after_update = user.point

    await update.message.reply_text(
        f"Successfully updated points for group '{group_name}' by + {points} - {current_points} for game {game_number}. points after update: {total_points_after_update}."
    )

@access_db
async def current_awarded_points_status_specific(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Session = None):
    """
    Command to check the current awarded points for a specific group and game.
    """
    user_id = update.effective_user.id
    role, _ = await db_utils.get_role(user_id, db=db)

    if role != Role.ADMIN:
        await update.message.reply_text(
            "You are not authorized to use this command."
        )
        return

    try:
        parts = update.message.text.split()
        if len(parts) != 3:
            raise ValueError("Incorrect number of arguments.")

        _, group_name, game_number_str = parts
        game_number = int(game_number_str)
    except Exception as e:
        await update.message.reply_text(
            "Usage: /current_awarded_points <group_name> <game_number>\n"
            "Example: /current_awarded_points TeamA 2"
        )
        return

    current_points = game.get_awarded_points(group_name, game_number)

    await update.message.reply_text(
        f"Current awarded points for group '{group_name}' in game {game_number}: {current_points}."
    )

async def current_status_of_awarded_points_for_all_groups_and_games_grouped_by_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Command to check the current awarded points for all groups and games.
    Response grouped by group
    """
    message = "Current Awarded Points for All Groups and Games:\n"
    grouped_points = {}
    for (group_name, game_number), points in Game.awarded_game_points.items():
        if group_name not in grouped_points:
            grouped_points[group_name] = []
        grouped_points[group_name].append((game_number, points))

    for group_name, games in grouped_points.items():
        message += f"Group: {group_name}\n"
        for game_number, points in games:
            message += f"  Game: {game_number}, ==>>: {points}\n"

    await update.message.reply_text(
        message
    )
    
@access_db
async def add_game_admins(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Session = None):
    """
    ADMIN command to add game admins.
    Usage: /add_game_admin <username1> <username2> ...
    """
    user_id = update.effective_user.id
    role, _ = await db_utils.get_role(user_id, db=db)

    if role != Role.ADMIN:
        await update.message.reply_text(
            "You are not authorized to use this command."
        )
        return

    try:
        parts = update.message.text.split()
        if len(parts) < 2:
            raise ValueError("No usernames provided.")

        usernames = parts[1:]
    except Exception as e:
        await update.message.reply_text(
            "Usage: /add_game_admin <username1> <username2> ...\n"
            "Example: /add_game_admin GameAdmin1 GameAdmin2"
        )
        return

    for username in usernames:
        if not any(admin["username"] == username for admin in game.game_admins):
            game.game_admins.append({"username": username})

    await update.message.reply_text(
        f"Successfully added game admins: {', '.join(usernames)}."
    )
    
@access_db
async def remove_game_admins(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Session = None):
    """
    ADMIN command to remove game admins.
    Usage: /remove_game_admin <username1> <username2> ...
    """
    user_id = update.effective_user.id
    role, _ = await db_utils.get_role(user_id, db=db)

    if role != Role.ADMIN:
        await update.message.reply_text(
            "You are not authorized to use this command."
        )
        return

    try:
        parts = update.message.text.split()
        if len(parts) < 2:
            raise ValueError("No usernames provided.")

        usernames = parts[1:]
    except Exception as e:
        await update.message.reply_text(
            "Usage: /remove_game_admin <username1> <username2> ...\n"
            "Example: /remove_game_admin GameAdmin1 GameAdmin2"
        )
        return

    game.game_admins = [admin for admin in game.game_admins if admin["username"] not in usernames]

    await update.message.reply_text(
        f"Successfully removed game admins: {', '.join(usernames)}."
    )
    
@access_db
async def list_game_admins(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Session = None):
    """
    ADMIN command to list all current game admins.
    """
    user_id = update.effective_user.id
    role, _ = await db_utils.get_role(user_id, db=db)

    if role != Role.ADMIN:
        await update.message.reply_text(
            "You are not authorized to use this command."
        )
        return

    if not game.game_admins:
        await update.message.reply_text("There are currently no game admins.")
        return

    admin_usernames = [admin["username"] for admin in game.game_admins]
    await update.message.reply_text(
        "Current Game Admins:\n" + "\n".join("@" + username for username in admin_usernames)
    )



handler = ConversationHandler(
    entry_points=[CommandHandler("start",start_game)],
    states={
        State.GET_GROUP_NAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_group_name)],
        State.DISTRIBUTER:[MessageHandler(filters.TEXT & (~filters.COMMAND),distributer)],
        State.GAME22:[MessageHandler(filters.TEXT & (~filters.COMMAND),game22)],
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
handler5 = CommandHandler("all_users_status", all_users_status)
handler6 = CommandHandler("all_finishers_status", all_finishers_status)
handler7 = CommandHandler("update_point_force", update_group_point_for_game_even_if_already_awarded)
handler8 = CommandHandler("current_awarded_points", current_awarded_points_status_specific)
handler9 = CommandHandler("current_awarded_points_all", current_status_of_awarded_points_for_all_groups_and_games_grouped_by_groups)
handler10 = CommandHandler("add_game_admin", add_game_admins)
handler11 = CommandHandler("remove_game_admin", remove_game_admins)
handler12 = CommandHandler("list_game_admins", list_game_admins)
handler13 = CommandHandler("current_awarded_points_grouped", current_status_of_awarded_points_for_all_groups_and_games_grouped_by_groups)
register_handler(handler1)
register_handler(handler2)
register_handler(handler3)
register_handler(handler4)
register_handler(handler5)
register_handler(handler6)
register_handler(handler7)
register_handler(handler8)
register_handler(handler9)
register_handler(handler10)
register_handler(handler11)
register_handler(handler12)
register_handler(handler13)
register_handler(handler)
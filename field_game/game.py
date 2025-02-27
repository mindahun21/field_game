from enum import Enum
from sqlalchemy.orm import Session

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
    Update,
)

from app import db_utils
from app.db import access_db
from app.models import Role,User
from app.handlers import register_handler
from app.utils import cancel_conversation,invalid_message

class State(Enum):
    DISTRIBUTER=0
    FIRST_GAME=1
    
game = Game()


@access_db
async def start_game(update:Update,context:ContextTypes.DEFAULT_TYPE,db:Session=None):
    role, _ = await db_utils.get_role(update.effective_user.id,db=db)
    if role == Role.USER:        
      await update.message.reply_text(
          f"{game.ruls}"
      )
      await update.message.reply_text(
        "Enter the first game code to start. If you don't have it, please reach out to the game admins."
      )
      
    elif role == Role.ADMIN:
      await context.bot.send_message(
        update.effective_user.id,
        f"<pre>hello, {update.effective_user.username}:\nyou are admin</pre>",
        parse_mode="HTML"
      )
      return
      
      
    elif admin:= await game.is_admin(update.effective_user.username):
      user = User(
        username=admin["username"],
        user_id=update.effective_user.id,
        role=Role.ADMIN
      )
      await db_utils.add_obj(user,db=db)
      await context.bot.send_message(
        update.effective_user.id,
        f"<pre>hello, {update.effective_user.username}:\nyou are admin</pre>",
        parse_mode="HTML"
      )
      return
      
      
    elif role == Role.NONE:
      user = User(
          username=update.effective_user.username,
          user_id=update.effective_user.id,
          role=Role.USER
      )

      await db_utils.add_obj(user,db=db)
      await update.message.reply_text(
          f"{game.ruls}"
      )
      await update.message.reply_text(
        "Enter the first game code to start. If you don't have it, please reach out to the game admins."
      )

    return State.DISTRIBUTER


@access_db
async def distributer(update:Update,context:ContextTypes.DEFAULT_TYPE, db:Session=None):
  if update.message is not None:  # how this can be none
      code = update.message.text

  status = game.check_code(code)
  user = await db_utils.get_entry(User, db=db,user_id = update.effective_user.id)

  if status == 404:
    await update.message.reply_text(game.wrong_msg)
    return State.DISTRIBUTER
  

  if status == 200:
    game.finishers.append(user.user_id)
    await context.bot.send_message(
      update.effective_user.id,
      f"congradulations👏 your team finished the game\n your team rank is: {len(game.finishers)}",
      parse_mode="HTML"
    )
    return ConversationHandler.END

  elif status in range(1,6):
    question = game.games.get(str(status),False)
    await update.message.reply_text(f"{question}")

    if status == 1:
      return State.DISTRIBUTER
    elif status == 5:
      await send_game5(context=context,user_id=update.effective_user.id)
    puzzle = game.redirect_puzzle.get(str(status),False)
    await update.message.reply_text(f"{puzzle}")

  return State.DISTRIBUTER

@access_db
async def reset_game(update: Update, context: ContextTypes.DEFAULT_TYPE, db:Session =None):
  role, _ = await db_utils.get_role(update.effective_user.id,db=db)
  
  
  if role == Role.USER:
    await update.message.reply_text(
       "you can't use this command b/c you are a user"
    )
    return
  elif role == Role.NONE:
    await update.message.reply_text(
       "you are not registered use /start to register"
    )
    return
     

  await db_utils.delete_all_rows(User, db=db)
  user = User(
    username="Mindahun21",
    user_id=update.effective_user.id,
    role=Role.ADMIN
  )
  await db_utils.add_obj(user,db=db)
    
  game.reset()

  await context.bot.send_message(
     update.effective_user.id,
     text="the game is successfully reseted"
  )

# @access_db
# async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE, db:Session =None):
#   role, _ = await db_utils.get_role(update.effective_user.id,db=db)
#   if role == Role.USER:
#     await update.message.reply_text(
#        "you can't use this command b/c you are a user"
#     )
#     return
#   elif role == Role.NONE:
#     await update.message.reply_text(
#       "you are not registered use /start to register"
#     )
#     return
  

#   users = await db_utils.get_entries(User,db=db,role=Role.USER)
#   adminMessage = F"The Winners are:\n<pre>"
  
#   for index, user_id in enumerate(game.finishers):
#     matched_user = next((user for user in users if user.user_id == user_id), None)
#     if matched_user:
#         adminMessage += f"{index+1}. @{matched_user.username or 'no username'}\n"

#   adminMessage += "</pre>"
#   admin = await db_utils.get_entry(User,db=db,role=Role.ADMIN)
#   await context.bot.send_message(
#      admin.user_id,
#      text=adminMessage,
#      parse_mode="HTML"
#   )

   
handler = ConversationHandler(
    entry_points=[CommandHandler("start",start_game)],
    states={
        State.DISTRIBUTER:[MessageHandler(filters.TEXT & (~filters.COMMAND),distributer)],
    },
    fallbacks=[
        CommandHandler("cancel",cancel_conversation),
        MessageHandler(filters.ALL,invalid_message),
    ],
)


# handler1  = CommandHandler("result",show_result)
handler2 = CommandHandler("reset",reset_game)
# register_handler(handler1)
register_handler(handler2)
register_handler(handler)


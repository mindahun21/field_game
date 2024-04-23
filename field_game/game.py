import asyncio
from asyncore import poll
from enum import Enum
from sqlalchemy.orm import Session

from .data import *
from .utils import *

from telegram.ext import(
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    PollAnswerHandler,
    ContextTypes,
    filters,
)

from telegram import(
    Update,
    Poll,
)

from app import db_utils
from app.db import access_db
from app.models import Role,User
from app.handlers import register_handler
from app.utils import cancel_conversation,invalid_message

class State(Enum):
    DISTRIBUTER=0
    FIRST_GAME=1
    


@access_db
async def start_game(update:Update,context:ContextTypes.DEFAULT_TYPE,db:Session=None):
    role, _ = await db_utils.get_role(update.effective_chat.id,db=db)
    if role == Role.USER:        
        await update.message.reply_text(
            f"{ruls}"
        )
        return State.DISTRIBUTER
    elif role == Role.ADMIN:
        await update.message.reply_text(
            f"hello, ADMIN {update.effective_chat.username}:\nyou are admin"
        )
        return State.DISTRIBUTER
    elif admin:= await is_admin(update.message.from_user.username):
        user = User(
            username=admin["username"],
            chat_id=update.effective_chat.id,
            role="admin",
        )
        await db_utils.add_obj(user,db=db)
        await update.message.reply_text(
            f"hello, ADMIN {update.effective_chat.username}:\nyou are admin"
        )
        return State.DISTRIBUTER
    elif role == Role.NONE:
        user = User(
            username=update.message.from_user.username,
            chat_id=update.effective_chat.id,
            role="user",
        )

        await db_utils.add_obj(user,db=db)
        await update.message.reply_text(
            f"{ruls}"
        )
        return State.DISTRIBUTER

async def distributer(update:Update,context:ContextTypes.DEFAULT_TYPE):
    global winnum, group_divider
    if update.message is not None:
        code = update.message.text
    status = check_code(code)

    if status == 200:
        await winMsg(update)
        return ConversationHandler.END

        
    elif status == 404:
        await update.message.reply_text(wrong_msg)
    elif status in range(1,6):
        question = games.get(str(status),False)
        if status ==4:
            await sendGame4(update,context,update.message.chat_id)
        else:
            await update.message.reply_text(f"{question}")
        if status == 2:
            await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"{redirect_puzzle.get('2')[group_divider % 2]}"
            )
            group_divider+=1
        if status== 1:
            return State.FIRST_GAME
        
        return State.DISTRIBUTER
    
# ANS:ሐቀአሠኘሸቸሀመተረሰነበየለ
async def first_game(update:Update,context:ContextTypes.DEFAULT_TYPE):
    correct_ans=["ሐ","ቀ","አ","ሠ","ኘ","ሸ","ቸ","ሀ","መ","ተ","ረ","ሰ","ነ","በ","የ","ለ"]
    user_ans=update.message.text
    chat_id = update.message.chat_id
    global group_divider

    if "tryFirst" not in context.user_data:
        context.user_data["tryFirst"] = 0

    if user_ans[:3].lower() == "ans":
        res = check_ans(user_ans[4:],correct_ans)
        if res == "correct":
            choose =games.get("11")
            await update.message.reply_text(
                f"👏👏👏WELL DONE👏👏👏\n\n your team managed to get the correct oreder\n\n"
                )
        elif context.user_data["tryFirst"] == 1:
            await update.message.reply_text(
                "your team needs to wait for ⏳ 5 mins because your team can\'t get the correct order"
            )
            await asyncio.sleep(300)
        else:
            if res.startswith("wrong"):
                await update.message.reply_text(f"{res}")
            else:
                await update.message.reply_text(f"Order: {res}")
            
            await update.message.reply_text(
                f"❗❗your team have one chance use it if not your teem have ⏳5 min delay penality❗❗\n enter the answer again."
            )
            
            context.user_data["tryFirst"]+=1
            return State.FIRST_GAME
        
        await update.message.reply_text(
                f"{choose}"
            )
        return State.DISTRIBUTER
    else:
        await update.message.reply_text("🤔 ምን ?")
        return State.FIRST_GAME
        

# ANS:ሐቀሠሸሀመረሰበለ
# async def third_game(update:Update,context:ContextTypes.DEFAULT_TYPE):
#     correct_ans=["ሐ","ቀ","ሠ","ሸ","ሀ","መ","ረ","ሰ","በ","ለ"]
#     user_ans=update.message.text
#     global game4_voice
#     if "tryThird" not in context.user_data:
#         context.user_data["tryThird"] = 0

#     if user_ans[:3].lower() == "ans":
#         res = check_ans(user_ans[4:],correct_ans)
#         if res == "correct" or not res.startswith("wrong") and int(res)>7:
#             await update.message.reply_text(
#                 f"👏👏👏WELL DONE👏👏👏\n\n your team managed to get the correct answer\n\n"
#                 )
#             await sendGame4(update,context,update.message.chat_id,)
#             return State.DISTRIBUTER
        
#         elif context.user_data["tryThird"] == 1:
#             await update.message.reply_text(
#                 "your team needs to wait for ⏳ 5 mins because your team can\'t get the correct answer"
#             )
#             await asyncio.sleep(300)
#             await sendGame4(update,context,update.message.chat_id,)
#             return State.DISTRIBUTER
        
#         else:
#             await update.message.reply_text(f"Correct: {res}\n\n❗❗your team have one chance use it if not your teem have ⏳5 min delay penality❗❗\n enter the answer again.")
#             context.user_data["tryThird"]+=1
#             return State.THIRD_GAME
        
#     else:
#         await update.message.reply_text("🤔 ምን ?")
#         return State.THIRD_GAME
     

handler = ConversationHandler(
    entry_points=[CommandHandler("start",start_game)],
    states={
        State.DISTRIBUTER:[MessageHandler(filters.TEXT & (~filters.COMMAND),distributer)],
        State.FIRST_GAME:[MessageHandler(filters.TEXT & (~filters.COMMAND),first_game)],
    },
    fallbacks=[
        CommandHandler("cancel",cancel_conversation),
        MessageHandler(filters.ALL,invalid_message),
    ],
)
register_handler(handler)


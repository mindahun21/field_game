import time
import asyncio
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
from app.models import Quiz
from app.utils import cancel_conversation,invalid_message

class State(Enum):
    DISTRIBUTER=0
    FIRST_GAME=1
    SECOND_GAME=2
    THIRD_GAME=3
    FOURTH_GAME=4
    FIFTH_GAME=5
    NEXT_GAME=6


@access_db
async def start_game(update:Update,context:ContextTypes.DEFAULT_TYPE,db:Session=None):
    role, _ = await db_utils.get_role(update.effective_chat.id,db=db)
    if role == Role.USER:        
        await update.message.reply_text(
            f"{ruls}"
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
            f"{ruls}"
        )

async def distributer(update:Update,context:ContextTypes.DEFAULT_TYPE):
    code = update.message.text
    status = check_code(code)

    if status == 100:
        await update.message.reply_text(
            f"👏👏👏 your teem finished {winnum}"
        )
        winnum+=1
    elif status == 404:
        await update.message.reply_text(wrong_msg)
    elif status in range(1,5):
        question = games.get(str(status),False)
        await update.message.reply_text(f"{question}")
        if status==2 or status==4:
            return State.DISTRIBUTER
        return State(status)
    
async def send_poll(context,update,game):
    await context.bot.send_poll(
        chat_id =update.message.chat_id,
        question=game[0],
        options=game[1],
        type=Poll.QUIZ,
        correct_option_id=game[2],
        is_anonymous=False,
    )

async def first_game(update:Update,context:ContextTypes.DEFAULT_TYPE):
    correct_ans=["ሐ","ቀ","አ","ሠ","ኘ","ሸ","ቸ","ሀ","መ","ተ","ረ","ሰ","ነ","በ","የ","ለ"]
    user_ans=update.message.text

    if not context.user_data["tryFirst"]:
        context.user_data["tryFirst"]=0

    game =games.get("11")
    if user_ans[:3].lower() == "ans":
        res = check_ans(user_ans[4:],correct_ans)
        if res == "correct":
            await update.message.reply.text(
                f"👏👏👏WELL DONE👏👏👏\n\n your team managed to get the correct oreder\n\n"
                )
            await send_poll(context,update,game)
            return State.NEXT_GAME
        
        elif context.user_data["tryFirst"] == 1:
            update.message.reply_text(
                "your team needs to wait for ⏳ 5 mins because your team can\'t get the correct order"
            )
            await asyncio.sleep(300)
            await send_poll(context,update,game)
            return State.NEXT_GAME
        
        else:
            await update.message.reply.text(f"Order: {res}")
            context.user_data["tryFirst"]+=1
            return State.FIRST_GAME
        
temp =0
async def next_game(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if not context.user_data["tryNext"]:
        context.user_data["tryNext"] = 0

    chat_id= update.pll.user.id
    game =games.get("11")

    if update.poll_answer.option_ids[0]== game[2]:
        await update.message.reply.text(
            f"👏👏👏CORRECT👏👏👏\n\n {redirect_puzzle.get("2")[temp % 2]}"
        )
        temp+=1
        return State.DISTRIBUTER
    elif context.user_data["tryNext"] == 1:
        update.message.reply_text(
                "your team missed chance so WAIT for ⏳ 5 mins to next game hint..."
            )
        await asyncio.sleep(300)
        await update.message.reply_text(
            f"{redirect_puzzle.get("2")[temp % 2]}"
        )
        temp+=1
        return State.DISTRIBUTER
    else:
        await update.message.reply_text(
            f"❗❗your team have one chance use it if not your teem have ⏳5 min delay penality❗❗\n enter the answer again."
        )
        await send_poll(context,update,game)
        return State.NEXT_GAME

async def second_game(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏃🏃enter game 3 code🏃🏃"
    )
    return State.DISTRIBUTER

async def third_game(update:Update,context:ContextTypes.DEFAULT_TYPE):
    correct_ans=["ሐ","ቀ","ሠ","ሸ","ሀ","መ","ረ","ሰ","በ","ለ"]
    user_ans=update.message.text
    if not context.user_data["tryThird"]:
        context.user_data["tryThird"]=0

    if user_ans[:3].lower() == "ans":
        res = check_ans(user_ans[4:],correct_ans)
        if res == "correct" or int(res)>7:
            await update.message.reply.text(
                f"👏👏👏WELL DONE👏👏👏\n\n your team managed to get the correct answer\n\n"
                )
            await update.message.reply_text(redirect_puzzle.get("4")[0])
            return State.DISTRIBUTER
        
        elif context.user_data["tryThird"] == 1:
            update.message.reply_text(
                "your team needs to wait for ⏳ 5 mins because your team can\'t get the correct answer"
            )
            await asyncio.sleep(300)
            await update.message.reply_text(redirect_puzzle.get("4")[0])
            return State.DISTRIBUTER
        
        else:
            await update.message.reply.text(f"Correct: {res}\n\n❗❗your team have one chance use it if not your teem have ⏳5 min delay penality❗❗\n enter the answer again.")
            context.user_data["tryThird"]+=1
            return State.THIRD_GAME
    



async def fourth_game(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("enter game 5 code")
    return State.DISTRIBUTER

# async def fifth_game(update:Update,context:ContextTypes.DEFAULT_TYPE):
    




handler = ConversationHandler(
    entry_points=[CommandHandler("start",start_game)],
    states={
        State.DISTRIBUTER:[MessageHandler(filters.TEXT & (~filters.COMMAND),distributer)],
        State.FIRST_GAME:[MessageHandler(filters.TEXT & (~filters.COMMAND),first_game)],
        State.SECOND_GAME:[MessageHandler(filters.TEXT & (~filters.COMMAND),second_game)],
        State.THIRD_GAME:[MessageHandler(filters.TEXT & (~filters.COMMAND),third_game)],
        State.FOURTH_GAME:[MessageHandler(filters.TEXT & (~filters.COMMAND),fourth_game)],
        # State.FIFTH_GAME:[MessageHandler(filters.TEXT & (~filters.COMMAND),fifth_game)],
        State.NEXT_GAME:[PollAnswerHandler(next_game)]
    },
    fallbacks=[
        CommandHandler("cancel",cancel_conversation),
        MessageHandler(filters.ALL,invalid_message),
    ],
)



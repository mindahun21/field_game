from enum import Enum

from sqlalchemy.orm import Session

from app.handlers import register_handler
from app.models import Quiz, Role,Question
from app import db_utils
from app.utils import cancel_conversation, invalid_message
from app.db import access_db

from telegram import (
    Update
)


from telegram.ext import (
     ConversationHandler,
     CommandHandler,
     MessageHandler,
     filters,
     ContextTypes,
)

class State(Enum):
    NAME =1
    SUBJECT = 2
    STOP_ADDING=3
    QUESTION = 4
    OPTIONS =5
    ANSWER =6


@access_db
async def ask_name(update:Update, context:ContextTypes.DEFAULT_TYPE,db:Session=None):
    role,_ = db_utils.get_role(update.effective_chat.id,db=db)

    if role != Role.ADMIN:
        await update.message.reply_text("Restricted only for admins")
        return

    await update.message.reply_text("Enter Descriptive name for your Quiz.")

    return State.NAME

@access_db
async def get_name(update:Update,context:ContextTypes.DEFAULT_TYPE, db:Session=None):
    name=update.message.text
    quiz = await db_utils.get_entry(Quiz,db=db,name=name)
    if quiz:
        await update.message.reply_text(
            f"{name} is already used, please Enter different name for your quiz"
        )
        return State.NAME
    
    context.user_data["name"] =name
    await update.message.reply_text("Enter Subject of the quiz: ")

    return State.SUBJECT

@access_db
async def get_subject(update:Update,context:ContextTypes.DEFAULT_TYPE,db:Session=None):
    quiz =Quiz(
        name=context.user_data["name"],
        subject=update.message.text,
    )

    await db_utils.add_obj(quiz,db=db)
    await update.message.reply_text(
        f"QUIZ: {context.user_data["name"]} is successfully created.\nif you want to add questions in the quiz,please Enter First Question\nor if you want to cancel hear use /stop command."
    )
    context.user_data["quiz"]=quiz

    return State.QUESTION

async def get_question(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data["question"]= update.message.text
    await update.message.reply_text("Enter the options (comma-separated):")

    return State.OPTIONS

async def get_options(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data["options"] = update.message.text.split(",")
    await update.message.reply_text("Enter the Index of Correct Answer:")

    return State.ANSWER

@access_db
async def get_answer(update:Update, context:ContextTypes.DEFAULT_TYPE,              db:Session=None):
    question = Question(
        question=context.user_data['question'],
        option=context.user_data['options'],
        ans_index=context.user_data['ans'],
        quiz_id=context.user_data["quiz"].id
    )
    await db_utils.add_obj(question,db=db)
    await update.message.reply_text("question added successfully\nif you wana to stop use /cancel command\nOR enter question to add another question")

    return State.QUESTION

handler = ConversationHandler(
    entry_points=[CommandHandler("create_quiz",ask_name)],
    states={
        State.NAME:[MessageHandler(filters.TEXT,get_name)],
        State.SUBJECT:[MessageHandler(filters.TEXT,get_subject)],
        State.QUESTION:[MessageHandler(filters.TEXT,get_question)],
        State.OPTIONS:[MessageHandler(filters.TEXT,get_options)],
        State.ANSWER:[MessageHandler(filters.TEXT,get_answer)],
    },
    fallbacks=[
        CommandHandler("cancel",cancel_conversation),
        MessageHandler(filters.ALL,invalid_message),
    ],

)

register_handler(handler)
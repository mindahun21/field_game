from sqlalchemy.orm import Session
from enum import Enum
from telegram import(
    ReplyKeyboardMarkup,
    Update,
)

from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,

    filters,
)

from app.utils import cancel_conversation, invalid_message
from app.db import access_db
from app import db_utils
from app.models import Quiz, Question
from app.handlers import register_handler

class State(Enum):
    CHOOSE_QUIZ=1
    QUESTION=2
    OPTIONS=3
    ANSWER=4

@access_db
async def choose_quiz(update:Update, context:ContextTypes.DEFAULT_TYPE, db:Session=None):
    quizes = await db_utils.get_entries(Quiz,db=db)

    quiz_names = [quiz.name for quiz in quizes]
    options =[[name] for name in quiz_names]

    replay_markup = ReplyKeyboardMarkup(options,one_time_keyboard=True)

    await update.message.reply_text("Choose Quiz: ",replay_markup=replay_markup)

    return State.CHOOSE_QUIZ

@access_db
async def choose_quiz_input(update:Update,context:ContextTypes.DEFAULT_TYPE, db:Session=None):
    selected = update.message.text
    selected_quiz = await db_utils.get_entry(selected_quiz,db=db,name=selected)

    if selected_quiz is None:
        return
    
    context.user_data["quiz"] = selected_quiz

    await update.message.reply_text(
        "Enter question: "
    )

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
        options=context.user_data['options'],
        ans_index=context.user_data['ans'],
        quiz_id=context.user_data["quiz"].id
    )
    await db_utils.add_obj(question,db=db)
    await update.message.reply_text("question added successfully\nif you wana to stop use /cancel command\nOR enter question to add another question")

    return State.QUESTION


handler = ConversationHandler(
    entry_points=[CommandHandler("add_question",choose_quiz)],
    states={
        State.CHOOSE_QUIZ:[MessageHandler(filters.TEXT,choose_quiz_input)],
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
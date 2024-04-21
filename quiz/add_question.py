from sqlalchemy.orm import Session
from enum import Enum
from telegram import(
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
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

    reply_markup = ReplyKeyboardMarkup(options,one_time_keyboard=True)

    message=await update.message.reply_text("Choose Quiz: ",reply_markup=reply_markup)

    context.user_data['previous_message']=message

    return State.CHOOSE_QUIZ

@access_db
async def choose_quiz_input(update:Update,context:ContextTypes.DEFAULT_TYPE, db:Session=None):
    selected = update.message.text
    selected_quiz = await db_utils.get_entry(Quiz,db=db,name=selected)

    if 'previous_message' in context.user_data:
        previous_message = context.user_data['previous_message']
        await previous_message.delete()

    if selected_quiz is None:
        return
    
    context.user_data["quiz"] = selected_quiz

    message = await context.bot.send_message(
        text="Enter question: ",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data['previous_message']=message

    return State.QUESTION


async def get_question(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data["question"]= update.message.text

    if 'previous_message' in context.user_data:
        previous_message = context.user_data['previous_message']
        await previous_message.delete()

    message = await update.message.reply_text("Enter the options (comma-separated):")
    context.user_data['previous_message']=message

    return State.OPTIONS

async def get_options(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data["options"] = update.message.text.split(",")

    if 'previous_message' in context.user_data:
        previous_message = context.user_data['previous_message']
        await previous_message.delete()

    message = await update.message.reply_text("Enter the Index of Correct Answer:")
    context.user_data['previous_message']=message

    return State.ANSWER

@access_db
async def get_answer(update:Update, context:ContextTypes.DEFAULT_TYPE,db:Session=None):
    if 'previous_message' in context.user_data:
        previous_message = context.user_data['previous_message']
        await previous_message.delete()

    question = Question(
        question=context.user_data['question'],
        options=context.user_data['options'],
        ans_index=int(update.message.text),
        quiz_id=context.user_data["quiz"].id
    )
    await db_utils.add_obj(question,db=db)
    await update.message.reply_text("question added successfully\nif you wana to stop use /cancel command\nOR enter question to add another question")

    return State.QUESTION


handler = ConversationHandler(
    entry_points=[CommandHandler("add_question",choose_quiz)],
    states={
        State.CHOOSE_QUIZ:[MessageHandler(filters.TEXT & (~filters.COMMAND),choose_quiz_input)],
        State.QUESTION:[MessageHandler(filters.TEXT & (~filters.COMMAND),get_question)],
        State.OPTIONS:[MessageHandler(filters.TEXT & (~filters.COMMAND),get_options)],
        State.ANSWER:[MessageHandler(filters.Regex(r'^\d+$') & (~filters.COMMAND),get_answer)],
    },
    fallbacks=[
        CommandHandler("cancel",cancel_conversation),
        MessageHandler(filters.ALL,invalid_message),
    ],
)


# register_handler(handler)
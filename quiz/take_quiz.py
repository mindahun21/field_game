import time
from enum import Enum
from sqlalchemy.orm import Session

from app import db_utils
from app.db import access_db
from app.handlers import register_handler
from app.models import Quiz
from app.utils import cancel_conversation,invalid_message

from telegram.ext import (
    ConversationHandler,
    PollAnswerHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
) 

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    Poll,
)

class State(Enum):
    CHOOSE_QUIZ=1
    # DISPLAY_QUIZ=2

quiz=None
questions =[]
user_answers =[]
start_time=None

def summary_msg()->str:
    correct_answers =0
    wrong_answers =0
    answered_questions =len(user_answers)

    for i in range(len(questions)):
        if i+1 <= answered_questions and user_answers[i]==questions[i].ans_index:
            correct_answers +=1
        else:
            wrong_answers +=1
    
    elapsed_time =time.time() - start_time
    elapsed_min = int(elapsed_time//60)
    elapsed_sec =int(elapsed_time % 60)
    time_msg=f"⏱{elapsed_min} min {elapsed_sec} sec"

    msg =f"Quiz {quiz.name} Completed!\n\n"
    msg+=f"✅Correct - {correct_answers}\n"
    msg+=f"❌Worong - {wrong_answers}\n"
    msg+=f"⌛️Missed - {len(questions) - answered_questions}\n\n"
    msg+=time_msg

    return msg

@access_db
async def choose_quiz(update:Update, context:ContextTypes.DEFAULT_TYPE, db:Session=None):
    quizes = await db_utils.get_entries(Quiz,db=db)

    quiz_names = [quiz.name for quiz in quizes]
    options =[[name] for name in quiz_names]

    reply_markup = ReplyKeyboardMarkup(options,one_time_keyboard=True)

    await update.message.reply_text("Choose Quiz: ",reply_markup=reply_markup)

    return State.CHOOSE_QUIZ

@access_db
async def choose_quiz_input(update:Update,context:ContextTypes.DEFAULT_TYPE, db:Session=None):
    chat_id = update.effective_chat.id
    selected = update.message.text
    selected_quiz = await db_utils.get_entry(Quiz,db=db,name=selected)

    if selected_quiz is None:
        return
    
    global quiz,questions,start_time
    quiz=selected_quiz
    questions = selected_quiz.questions
    # Remove the keyboard markup
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Quiz: {quiz.name} started!",
        reply_markup=ReplyKeyboardRemove(),
    )

    await context.bot.send_poll(
        chat_id=chat_id,
        question=f'1, {questions[0].question}',
        options=questions[0].options,
        type=Poll.QUIZ,
        correct_option_id=questions[0].ans_index,
        is_anonymous=False,
    )

    start_time =time.time()

    return ConversationHandler.END

async def display_questions(update:Update,context:ContextTypes.DEFAULT_TYPE):
    chat_id = update.poll_answer.user.id
    global quiz, questions, user_answers, start_time

    answer=update.poll_answer
    user_answers.append(answer.option_ids[0])

    question_number =len(user_answers)

    if question_number < len(questions):
        question = questions[question_number]
        await context.bot.send_poll(
            chat_id=chat_id,
            question=f'{question_number+1}, {question.question}',
            options=question.options,
            type=Poll.QUIZ,
            correct_option_id=question.ans_index,
            is_anonymous=False,
        )

    else:
        msg =summary_msg()
        await context.bot.send_message(
            chat_id=chat_id,
            text=msg,
        )
        quiz=None
        questions =[]
        user_answers =[]
        start_time=None
    


handler = ConversationHandler(
    entry_points=[CommandHandler("take_quiz",choose_quiz)],
    states={
        State.CHOOSE_QUIZ:[MessageHandler(filters.TEXT,choose_quiz_input)],
        # State.DISPLAY_QUIZ:[PollAnswerHandler(display_questions)]
    },
    fallbacks=[
        CommandHandler("cancel",cancel_conversation),
        MessageHandler(filters.ALL,invalid_message),
    ],
)

poll_handler = PollAnswerHandler(display_questions)
# register_handler(poll_handler)
# register_handler(handler)
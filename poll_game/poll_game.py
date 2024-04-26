from enum import Enum
from datetime import datetime

from sqlalchemy.orm import Session
from telegram import(
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    Poll,
)

from telegram.ext import(
    CallbackQueryHandler,
    CommandHandler,
    PollAnswerHandler,
    ContextTypes,
    CallbackContext,
)

from app.utils import cancel_conversation, invalid_message
from app.handlers import register_handler
from app.models import Quiz, PollRank, User
from app import db_utils
from app.db import access_db

quiz_started = False

@access_db
async def update_user_rank(context,user,db:Session= None):
    start_time = context.user_data["start_time"]
    end_time = datetime.now()
    temp = end_time - start_time
    duration = int(temp.total_seconds())

    questions = context.user_data["questions"]
    user_answers = context.user_data["user_answers"]

    correct_answer_count =0
    wrong_answer_count = 0
    answered_ques_count = len(user_answers)

    for i in range(len(questions)):
        if i+1 <= answered_ques_count and user_answers[i]==questions[i].ans_index:
            correct_answer_count +=1
        else:
            wrong_answer_count +=1

    poll_rank= PollRank(user_id =user.id, score=correct_answer_count, duration=duration, end_time=end_time)
    await db_utils.add_obj(poll_rank,db=db)

    msg=f"Quiz {context.user_data['quiz'].name} complete\n\n\n"
    msg+=f"✅Correct - {correct_answer_count}\n"
    msg+=f"❌Worong - {wrong_answer_count}\n\n"
    msg+=f"⌛️Missed - {len(questions) - answered_ques_count} \n"
    msg+=f"⏱{duration // 60} min {duration%60} sec"
    
    await context.bot.send_message(chat_id=user.chat_id, text =msg)
    context.user_data.clear()
    context.user_data["correct"] = correct_answer_count

@access_db
async def start_quiz(update: Update, context: CallbackContext, db:Session = None):
    global quiz_started
    chat_id = update.effective_chat.id
    if not quiz_started: 
        await context.bot.send_message(
            chat_id=chat_id,
            text="The QUIZ is not started please wait for it"
        )
        return
    
    quiz_name ="robel_quiz"
    selected_quiz = await db_utils.get_entry(Quiz,db=db,name=quiz_name)
    context.user_data["quiz"]=selected_quiz
    context.user_data["questions"] = selected_quiz.questions

    await context.bot.send_message(
        chat_id=chat_id,
        text =f"\n{selected_quiz.name} QUIZ started { 'AGAIN' if update.callback_query =='try_again' else ''}!\n\n"
    )

    await context.bot.send_poll(
        chat_id=chat_id,
        question = f"1, {context.user_data['questions'][0].question}",
        options = context.user_data['questions'][0].options,
        type=Poll.QUIZ,
        correct_option_id=context.user_data['questions'][0].ans_index,
        is_anonymous=False
    )

    context.user_data["start_time"]=datetime.now()
    context.user_data["user_answers"] = []
        

@access_db
async def handle_quiz(update:Update, context:CallbackContext,db:Session =None):
    user_id = update.poll_answer.user.id
    user = await db_utils.get_entry(User,db=db,user_id=user_id)

    # accept answer
    context.user_data["user_answers"].append(update.poll_answer.option_ids[0])
    question_num = len(context.user_data["user_answers"])
    questions = context.user_data["questions"]

    # display the nxt quiz
    if question_num < len(questions):
        question = questions[question_num]
        await context.bot.send_poll(
            chat_id=user_id,
            question =f"{question_num+1}, {question.question}",
            options=question.options,
            type= Poll.QUIZ,
            correct_option_id=question.ans_index,
            is_anonymous=False,
        )
    else:
        await update_user_rank(context,user)
            

@access_db
async def send_quiz_rank(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Session = None):
    global quiz_started 
    quiz_started =False
    ranked_poll_ranks = db.query(PollRank).order_by(PollRank.score.desc(), PollRank.end_time.asc()).all()   


    header = f"| {'Username':<{20}} | {'Score':<{15}} | {'End time':<{20}} | {'Rank':<{10}} |\n"
    top_scorers = ""
    rank = 1

    for poll_rank in ranked_poll_ranks:
        username = poll_rank.user.username
        score = poll_rank.score
        end_time = poll_rank.end_time

        row = f"| @{username} | {score}| {end_time.strftime('%H:%M:%S')}  | {rank} |\n"
        
        if rank < 20:
            top_scorers += row
            
        await context.bot.send_message(
            chat_id=poll_rank.user.chat_id,
            text=f"{header}\n{row}"
        )
        rank += 1
    
    admins = await db_utils.get_entries(User, db=db, role="admin")
    
    if admins:
        for admin in admins:
            await context.bot.send_message(
                chat_id=admin.chat_id,
                text=f"=====TOP SCORERS=====\n{header}\n{top_scorers}"
            )

    await db_utils.delete_all_rows(PollRank, db=db)


@access_db
async def make_quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE,db:Session= None):
    global quiz_started 
    if not quiz_started:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The quiz has been started")
        quiz_started = True


start_poll_handler = CommandHandler("start_quiz",start_quiz)
poll_handler = PollAnswerHandler(handle_quiz)
start_quiz_handler = CommandHandler("make_quiz_start",make_quiz_start)
stop_quiz_handler = CommandHandler("stop_quiz",send_quiz_rank)

register_handler(start_poll_handler)
register_handler(poll_handler)
register_handler(start_quiz_handler)
register_handler(stop_quiz_handler)
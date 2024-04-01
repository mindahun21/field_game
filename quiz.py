import logging

from telegram import(
    Update,
    Poll,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    CallbackContext,
    Application,
    CommandHandler,
    PollAnswerHandler,
    ConversationHandler,
    filters,
    MessageHandler,
    CallbackQueryHandler
)
TOKEN = '6551771883:AAE81SzHUq6PlkQ-FMRWYRZVjRbJ9VyVsdo'


class Question:
    def __init__(self, question, options, ans):
        self.question = question
        self.options = options
        self.ans = ans

QUESTIONS = [
    Question('What is the capital of France?', ["Paris", "London", "Berlin"], 0),
    Question('Which planet is known as the Red Planet?', ["Mars", "Jupiter", "Venus"], 0),
]

QUIZE_COUNT = len(QUESTIONS)
ENTER_QUESTION, ENTER_OPTIONS, ENTER_ANSWER = range(3)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

user_answers=[]


def quiz_summary()->str:
    correct_answers = 0
    wrong_answers = 0
    answered_questions = len(user_answers)

    for i in range(QUIZE_COUNT):
        if i+1 <= answered_questions and user_answers[i] == QUESTIONS[i].ans:
            correct_answers +=1
        else:
            wrong_answers+=1
    
    summary_message = f"Quiz completed!\n\nCorrect answers: {correct_answers}💪\nWrong answers: {wrong_answers}🧐\nAnswered questions: {answered_questions}\nFinal {correct_answers}/{answered_questions}\n"

    return summary_message

async def start(update:Update , context:ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == '/stop':
        if len(user_answers) > 0:
            summary_message = quiz_summary()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=summary_message,
            )
        user_answers.clear()
        await update.message.reply_text("Quiz stopped. You can start a new quiz using /quiz.")
    else:
        await update.message.reply_text("Please select /quiz to start a new quiz or /stop to stop the current quiz.")


async def start_quiz(update: Update,context:CallbackContext) -> None:
    user_answers.clear()

    question_number = 1
    question = QUESTIONS[question_number-1]

    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=f"QUIZ {question_number}: {question.question}",
        options=question.options,
        type=Poll.QUIZ,
        correct_option_id=question.ans,
        is_anonymous=False,
    )

async def receive_quiz_answer(update: Update, context: CallbackContext) -> None:
    print("function invocked")
    answer = update.poll_answer
    user_answers.append(answer.option_ids[0])

    chat_id = update.poll_answer.user.id

    if len(user_answers) < QUIZE_COUNT:
        question_number = len(user_answers) + 1
        question = QUESTIONS[question_number-1] 

        await context.bot.send_poll(
            chat_id=chat_id,
            question=f"QUIZ {question_number}: {question.question}",
            options=question.options,
            type=Poll.QUIZ,
            correct_option_id=question.ans,
            is_anonymous=False,
        )
    else:
        summary=quiz_summary()
        await context.bot.send_message(
            chat_id=chat_id,
            text=summary,
        )

async def add_question(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "add_question":
        await update.effective_message.reply_text("Let's add a new question.\n\nEnter the question:")
    return ENTER_QUESTION

async def add_question_input(update: Update, context: CallbackContext):
    context.user_data['question'] = update.message.text
    update.message.reply_text("Enter the options (comma-separated):")
    return ENTER_OPTIONS

async def add_options_input(update: Update, context: CallbackContext):
    context.user_data['options'] = update.message.text.split(",")
    update.message.reply_text("Enter the index of the correct answer:")
    return ENTER_ANSWER

async def add_answer_input(update: Update, context: CallbackContext):
    context.user_data['ans'] = int(update.message.text)

    question = Question(
        context.user_data['question'],
        context.user_data['options'],
        context.user_data['ans']
    )
    QUESTIONS.append(question)

    update.message.reply_text("Question added successfully!")

    return ConversationHandler.END


async def cancel_add_question(update: Update, context: CallbackContext):
    await update.message.reply_text("Question addition cancelled.")
    return ConversationHandler.END

add_question_handler = ConversationHandler(
    entry_points=[CommandHandler("add_question", add_question)],
    states={
        ENTER_QUESTION: [MessageHandler(filters.Text, add_question_input)],
        ENTER_OPTIONS: [MessageHandler(filters.Text, add_options_input)],
        ENTER_ANSWER: [MessageHandler(filters.Text, add_answer_input)],
    },
    fallbacks=[CommandHandler("cancel", cancel_add_question)],
)

async def manage_quiz(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Add Question", callback_data="add_question")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Click the 'Add Question' button to add a new question:", reply_markup=reply_markup)


def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start",start))
    application.add_handler(CommandHandler("quiz",start_quiz))
    application.add_handler(CommandHandler("stop",start))
    application.add_handler(CommandHandler("manage_quiz",manage_quiz))
    application.add_handler(PollAnswerHandler(receive_quiz_answer))

    application.add_handler(add_question_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

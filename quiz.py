import logging

from telegram import(
    Update,
    KeyboardButtonPollType,
    Poll,
)
from telegram.ext import (
    ContextTypes,
    CallbackContext,
    Application,
    CommandHandler,
    PollHandler,
)

QUIZE_COUNT = 10
QUESTIONS = [
    ['What is the capital of France?', ["Paris", "London", "Berlin"]],
    ['Which planet is known as the Red Planet?', ["Mars", "Jupiter", "Venus"]],
    ['Who painted the Mona Lisa?', ["Leonardo da Vinci", "Pablo Picasso", "Vincent van Gogh"]],
    ['What is the largest ocean on Earth?', ["Pacific Ocean", "Indian Ocean", "Atlantic Ocean"]],
    ['Who wrote the play "Romeo and Juliet"?', ["William Shakespeare", "Jane Austen", "Charles Dickens"]],
    ['Which country is famous for the Great Wall?', ["China", "India", "Russia"]],
    ['What is the chemical symbol for gold?', ["Au", "Ag", "Fe"]],
    ['Who invented the telephone?', ["Alexander Graham Bell", "Thomas Edison", "Albert Einstein"]],
    ['Which animal is known as the "King of the Jungle"?', ["Lion", "Tiger", "Leopard"]],
    ['What is the tallest mountain in the world?', ["Mount Everest", "K2", "Makalu"]],
]

TOKEN = '6551771883:AAE81SzHUq6PlkQ-FMRWYRZVjRbJ9VyVsdo'

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update:Update , context:ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "please select /quiz to start new quiz"
    )


user_answers=[]

async def start_quiz(update: Update,context:CallbackContext) -> None:
    user_answers.clear()

    question_number = 1
    question = QUESTIONS[question_number]

    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=f"QUIZ {question_number}: {question[0]}",
        options=question[1],
        type=Poll.QUIZ,
        is_anonymous=False,
    )

async def receive_quiz_answer(update:Update, context:CallbackContext) -> None:
    answer=update.poll_answer
    user_answers.append(answer.option_ids[0])

    if len(user_answers) < QUIZE_COUNT:
        question_number = len(user_answers) + 1
        question = QUESTIONS[len(user_answers)]

        await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=f"QUIZ {question_number}: {question[0]}",
            options=question[1],
            type=Poll.QUIZ,
            is_anonymous=False,
        ) 
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Quiz completed! Here are your answers:\n" + "\n".join(user_answers),
        )

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start",start))
    application.add_handler(CommandHandler("quiz",start_quiz))
    application.add_handler(PollHandler(receive_quiz_answer))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

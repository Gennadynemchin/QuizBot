import logging
import redis
from enum import Enum, auto
from get_question import get_random_question
from telegram import ReplyKeyboardMarkup, Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, ConversationHandler, filters
from credentials import telegram_token, redis_login, redis_password, redis_host

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

redis_db = redis.Redis(host=redis_host,
                       port=14083,
                       username=redis_login,
                       password=redis_password,
                       decode_responses=True)


class State(Enum):
    NEW_QUESTION = auto()
    ANSWER = auto()
    GIVE_UP = auto()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [['New question', 'Give up'], ['Show result']]
    markup = ReplyKeyboardMarkup(keyboard)
    await update.message.reply_text('Hello and welcome!', reply_markup=markup)
    return State.NEW_QUESTION


async def new_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user.id
    question, answer = get_random_question()
    redis_db.set(str(user), answer)
    await update.message.reply_text(question)
    return State.ANSWER


async def get_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = str(update.effective_user.id)
    user_text = update.message.text
    answer = redis_db.get(user)
    if user_text.lower() == answer.lower():
        await update.message.reply_text("Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»")
        return State.NEW_QUESTION
    else:
        await update.message.reply_text("Неправильно… Попробуешь ещё раз?")
        return State.GIVE_UP


def main() -> None:
    application = Application.builder().token(telegram_token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            State.NEW_QUESTION: [MessageHandler(filters.Regex(r"New question"), new_question)],
            State.ANSWER: [MessageHandler(filters.TEXT, get_answer)],
            State.GIVE_UP: [MessageHandler(filters.TEXT, get_answer)]},
        fallbacks=[])
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()

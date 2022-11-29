import logging
import redis
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from get_question import get_random_question
from credentials import telegram_token, redis_login, redis_password, redis_host


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

redis_db = redis.Redis(host=redis_host,
                       port=14083,
                       username=redis_login,
                       password=redis_password,
                       decode_responses=True)


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Показать результаты']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Hi!', reply_markup=reply_markup)


def new_question(bot, update):
    question, answer = get_random_question()
    user = str(update.message.from_user)
    redis_db.set(user, answer)
    update.message.reply_text(question)


def get_answer(bot, update):
    user = str(update.message.from_user)
    answer = redis_db.get(user)
    update.message.reply_text(answer)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(telegram_token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex(r"Новый вопрос"), new_question))
    dp.add_handler(MessageHandler(Filters.regex(r"Сдаться"), get_answer))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

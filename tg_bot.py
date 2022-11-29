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
    redis_db.set(f'{user}_question', question)
    redis_db.set(f'{user}_answer', answer)
    if redis_db.get(f'{user}_score') is None:
        redis_db.set(f'{user}_score', 0)
    update.message.reply_text(question)


def give_up(bot, update):
    user = str(update.message.from_user)
    answer = redis_db.get(f'{user}_answer')
    update.message.reply_text(answer)


def get_score(bot, update):
    user = str(update.message.from_user)
    score = redis_db.get(f'{user}_score')
    update.message.reply_text(score)


def get_answer(bot, update):
    user = str(update.message.from_user)
    user_answer = str(update.message)
    right_answer = redis_db.get(f'{user}_answer')
    score = int(redis_db.get(f'{user}_score'))
    if str(right_answer).find(str(user_answer)):
        update.message.reply_text('Correct!')
        redis_db.set(f'{user}_score', score+1)
    else:
        update.message.reply_text('Naaah!')


def main():
    updater = Updater(telegram_token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex(r"Новый вопрос"), new_question))
    dp.add_handler(MessageHandler(Filters.regex(r"Сдаться"), give_up))
    dp.add_handler(MessageHandler(Filters.regex(r"Показать результаты"), get_score))
    dp.add_handler(MessageHandler(Filters.text, get_answer))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

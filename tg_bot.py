import logging
import redis
from enum import Enum, auto
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
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


class State(Enum):
    NEW_QUESTION = auto()
    ANSWER_ATTEMPT = auto()
    GIVE_UP = auto()


def start(bot, update):
    user = update.message.from_user
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Показать результаты']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Hi!', reply_markup=reply_markup)
    redis_db.set(f'{user}_score', 0)
    return State.NEW_QUESTION


def handle_new_question_request(bot, update):
    question, answer = get_random_question()
    user = update.message.from_user
    redis_db.set(f'{user}_question', question)
    redis_db.set(f'{user}_answer', answer)
    update.message.reply_text(question)
    return State.ANSWER_ATTEMPT


def handle_solution_attempt(bot, update):
    user = update.message.from_user
    user_answer = update.message.text.lower()
    right_answer = redis_db.get(f'{user}_answer').replace('.', '#'). \
        replace('(', '#'). \
        replace('"', ''). \
        split('#')[0].lower()
    score = redis_db.get(f'{user}_score')
    if user_answer == right_answer:
        score = int(score) + 1
        redis_db.set(f'{user}_score', score)
        update.message.reply_text(f'Абсолютно верно! Ваш счет: {score}')
        return State.NEW_QUESTION
    else:
        update.message.reply_text('К сожалению, это неправильный ответ')
        return State.GIVE_UP


def give_up(bot, update):
    user = update.message.from_user
    answer = redis_db.get(f'{user}_answer')
    update.message.reply_text(answer)
    return State.NEW_QUESTION


def get_score(bot, update):
    user = update.message.from_user
    score = redis_db.get(f'{user}_score')
    update.message.reply_text(f'Ваш счет: {score}')


def reset_score(bot, update):
    user = update.message.from_user
    redis_db.set(f'{user}_score', 0)
    score = redis_db.get(f'{user}_score')
    update.message.reply_text(f'Счет сброшен. Текущий счет: {score}')


def main():
    updater = Updater(telegram_token)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={State.NEW_QUESTION: [MessageHandler(Filters.regex(r'Новый вопрос'), handle_new_question_request),
                                     MessageHandler(Filters.regex(r'Показать результаты'), get_score)],

                State.ANSWER_ATTEMPT: [MessageHandler(Filters.regex(r'Сдаться'), give_up),
                                       MessageHandler(Filters.regex(r'Показать результаты'), get_score),
                                       MessageHandler(Filters.text, handle_solution_attempt)],

                State.GIVE_UP: [MessageHandler(Filters.regex(r'Сдаться'), give_up),
                                MessageHandler(Filters.regex(r'Показать результаты'), get_score),
                                MessageHandler(Filters.text, handle_solution_attempt)]
                },
        fallbacks=[CommandHandler('reset', reset_score)])

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

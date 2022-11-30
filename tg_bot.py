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
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Показать результаты']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Hi!', reply_markup=reply_markup)
    return State.NEW_QUESTION


def handle_new_question_request(bot, update):
    question, answer = get_random_question()
    user = str(update.message.from_user)
    redis_db.set(f'{user}_question', question)
    redis_db.set(f'{user}_answer', answer)
    update.message.reply_text(question)
    return State.ANSWER_ATTEMPT


def handle_solution_attempt(bot, update):
    user = str(update.message.from_user)
    user_answer = str(update.message.text)
    right_answer = redis_db.get(f'{user}_answer')
    if user_answer.lower() == right_answer.lower():
        update.message.reply_text('Correct!')
        return State.NEW_QUESTION
    else:
        update.message.reply_text('Naaah!')
        return State.GIVE_UP


def give_up(bot, update):
    user = str(update.message.from_user)
    answer = redis_db.get(f'{user}_answer')
    update.message.reply_text(answer)
    return State.NEW_QUESTION


def get_score(bot, update):
    user = str(update.message.from_user)
    score = redis_db.get(f'{user}_score')
    update.message.reply_text(score)


def main():
    updater = Updater(telegram_token)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={State.NEW_QUESTION: [MessageHandler(Filters.regex(r'Новый вопрос'), handle_new_question_request),
                                     MessageHandler(Filters.regex(r'Показать результаты'), get_score)],

                State.ANSWER_ATTEMPT: [MessageHandler(Filters.text, handle_solution_attempt),

                                       MessageHandler(Filters.regex(r'Показать результаты'), get_score)],

                State.GIVE_UP: [MessageHandler(Filters.regex(r'Сдаться'), give_up),
                                MessageHandler(Filters.regex(r'Показать результаты'), get_score)]
                },

        fallbacks=[])

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

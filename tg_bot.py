import logging
from functools import partial
import os
import redis
from dotenv import load_dotenv
from enum import Enum, auto
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
from questions import get_random_question, \
    save_user_question, \
    create_new_user, \
    check_user_answer, \
    get_user_info, \
    giveup_user

logger = logging.getLogger(__name__)
messenger = 'tg'


class State(Enum):
    NEW_QUESTION = auto()
    ANSWER_ATTEMPT = auto()
    GIVE_UP = auto()


def start(bot, update, redis_db):
    user = update.effective_user.id
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Показать результаты']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Hi!', reply_markup=reply_markup)
    create_new_user(redis_db, messenger, user)
    return State.NEW_QUESTION


def handle_new_question_request(bot, update, redis_db):
    question, answer = get_random_question()
    user = update.effective_user.id
    save_user_question(redis_db, messenger, user, question, answer)
    update.message.reply_text(question)
    return State.ANSWER_ATTEMPT


def handle_solution_attempt(bot, update, redis_db):
    user = update.effective_user.id
    user_answer = update.message.text.lower()
    result = check_user_answer(redis_db, messenger, user, user_answer)
    if result:
        update.message.reply_text('Абсолютно верно!')
        return State.NEW_QUESTION
    else:
        update.message.reply_text('Это неправильный ответ. Попробуй еще раз')
        return State.GIVE_UP


def give_up(bot, update, redis_db):
    user = update.effective_user.id
    update.message.reply_text(giveup_user(redis_db, messenger, user))
    return State.NEW_QUESTION


def get_score(bot, update, redis_db):
    user = update.effective_user.id
    correct_answers, total_answers = get_user_info(redis_db, messenger, user)
    update.message.reply_text(f'Верных ответов: {correct_answers}\nВсего ответов: {total_answers}')


def reset_score(bot, update, redis_db):
    user = update.effective_user.id
    redis_db.set(f'{user}_score', 0)
    score = redis_db.get(f'{user}_score')
    update.message.reply_text(f'Счет сброшен. Текущий счет: {score}')


def main():
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    redis_login = os.getenv('REDIS_LOGIN')
    redis_password = os.getenv('REDIS_PASSWORD')
    redis_host = os.getenv('REDIS_HOST')
    redis_db = redis.Redis(host=redis_host,
                           port=14083,
                           username=redis_login,
                           password=redis_password,
                           decode_responses=True)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
    updater = Updater(telegram_token)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', partial(start, redis_db=redis_db))],
        states={State.NEW_QUESTION: [MessageHandler(Filters.regex(r'Новый вопрос'),
                                                    partial(handle_new_question_request,
                                                            redis_db=redis_db)),
                                     MessageHandler(Filters.regex(r'Показать результаты'),
                                                    partial(get_score,
                                                            redis_db=redis_db))],

                State.ANSWER_ATTEMPT: [MessageHandler(Filters.regex(r'Сдаться'),
                                                      partial(give_up,
                                                              redis_db=redis_db)),
                                       MessageHandler(Filters.regex(r'Показать результаты'),
                                                      partial(get_score,
                                                              redis_db=redis_db)),
                                       MessageHandler(Filters.text,
                                                      partial(handle_solution_attempt,
                                                              redis_db=redis_db))],

                State.GIVE_UP: [MessageHandler(Filters.regex(r'Сдаться'),
                                               partial(give_up,
                                                       redis_db=redis_db)),
                                MessageHandler(Filters.regex(r'Показать результаты'),
                                               partial(get_score,
                                                       redis_db=redis_db)),
                                MessageHandler(Filters.text,
                                               partial(handle_solution_attempt,
                                                       redis_db=redis_db))]
                },
        fallbacks=[CommandHandler('reset_score', partial(reset_score, redis_db=redis_db))])

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

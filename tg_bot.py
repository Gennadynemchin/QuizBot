import logging
import redis
from enum import Enum, auto
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
from questions import get_random_question, \
    save_user_question, \
    create_new_user, \
    check_user_answer, \
    get_user_info, \
    giveup_user
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
    user = update.effective_user.id
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Показать результаты']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Hi!', reply_markup=reply_markup)
    create_new_user(redis_db, 'tg', user)
    return State.NEW_QUESTION


def handle_new_question_request(bot, update):
    question, answer = get_random_question()
    user = update.effective_user.id
    save_user_question(redis_db, 'tg', user, question, answer)
    update.message.reply_text(question)
    return State.ANSWER_ATTEMPT


def handle_solution_attempt(bot, update):
    user = update.effective_user.id
    user_answer = update.message.text.lower()
    result = check_user_answer(redis_db, 'tg', user, user_answer)
    if result:
        update.message.reply_text('Абсолютно верно!')
        return State.NEW_QUESTION
    else:
        update.message.reply_text('Это неправильный ответ. Попробуй еще раз')
        return State.GIVE_UP


def give_up(bot, update):
    user = update.effective_user.id
    update.message.reply_text(giveup_user(redis_db, 'tg', user))
    return State.NEW_QUESTION


def get_score(bot, update):
    user = update.effective_user.id
    correct_answers, total_answers = get_user_info(redis_db, 'tg', user)
    update.message.reply_text(f'Верных ответов: {correct_answers}\nВсего ответов: {total_answers}')


def reset_score(bot, update):
    user = update.effective_user.id
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

import logging
from functools import partial
import os
import random
import redis
import json
from dotenv import load_dotenv
from enum import Enum, auto
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
from questions import check_user_answer

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
    key = f'user_{messenger}_{user}'
    value = json.dumps({"question": None,
                        "answer": None,
                        "correct_answers": 0,
                        "total_answers": 0}, ensure_ascii=False)
    redis_db.set(key, value)
    return State.NEW_QUESTION


def handle_new_question_request(bot, update, redis_db, questions_dict):
    question, answer = random.choice(list(questions_dict.items()))
    user = update.effective_user.id
    key = f'user_{messenger}_{user}'
    user_info = json.loads(redis_db.get(key))
    correct_answers = user_info['correct_answers']
    total_answers = user_info['total_answers']
    value = json.dumps({"question": question,
                        "answer": answer,
                        "correct_answers": correct_answers,
                        "total_answers": total_answers}, ensure_ascii=False)
    redis_db.set(key, value)
    update.message.reply_text(question)
    return State.ANSWER_ATTEMPT


def handle_solution_attempt(bot, update, redis_db):
    user = update.effective_user.id
    user_answer = update.message.text.lower()
    result, user_redis, user_redis_info = check_user_answer(redis_db, messenger, user, user_answer)
    if result:
        redis_db.set(user_redis, user_redis_info)
        update.message.reply_text('Абсолютно верно!')
        return State.NEW_QUESTION
    else:
        redis_db.set(user_redis, user_redis_info)
        update.message.reply_text('Это неправильный ответ. Попробуй еще раз')
        return State.GIVE_UP


def give_up(bot, update, redis_db):
    user = update.effective_user.id
    key = f'user_{messenger}_{user}'
    user_info = json.loads(redis_db.get(key))
    question = user_info['question']
    answer = user_info['answer']
    correct_answers = user_info['correct_answers']
    total_answers = user_info['total_answers']
    value = json.dumps({"question": question,
                        "answer": answer,
                        "correct_answers": correct_answers,
                        "total_answers": total_answers + 1}, ensure_ascii=False)
    redis_db.set(key, value)
    update.message.reply_text(answer)
    return State.NEW_QUESTION


def get_score(bot, update, redis_db):
    user = update.effective_user.id
    key = f'user_{messenger}_{user}'
    user_info = json.loads(redis_db.get(key))
    correct_answers = user_info['correct_answers']
    total_answers = user_info['total_answers']
    update.message.reply_text(f'Верных ответов: {correct_answers}\nВсего ответов: {total_answers}')


def reset_score(bot, update, redis_db):
    user = update.effective_user.id
    key = f'user_{messenger}_{user}'
    user_info = json.loads(redis_db.get(key))
    question = user_info['question']
    answer = user_info['answer']
    score = user_info['correct_answers']
    value = json.dumps({"question": question,
                        "answer": answer,
                        "correct_answers": 0,
                        "total_answers": 0}, ensure_ascii=False)
    redis_db.set(key, value)
    update.message.reply_text(f'Счет сброшен. Текущий счет: {score}')


def delete_user(bot, update, redis_db):
    user = update.effective_user.id
    key = f'user_{messenger}_{user}'
    return redis_db.delete(key)


def main():
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    redis_login = os.getenv('REDIS_LOGIN')
    redis_password = os.getenv('REDIS_PASSWORD')
    redis_host = os.getenv('REDIS_HOST')
    questions_path = os.getenv('QUESTIONS_PATH')
    redis_db = redis.Redis(host=redis_host,
                           port=14083,
                           username=redis_login,
                           password=redis_password,
                           decode_responses=True)
    with open(questions_path, 'r') as openfile:
        questions_dict = json.load(openfile)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
    updater = Updater(telegram_token)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', partial(start, redis_db=redis_db))],
        states={State.NEW_QUESTION: [MessageHandler(Filters.regex(r'Новый вопрос'),
                                                    partial(handle_new_question_request,
                                                            redis_db=redis_db, questions_dict=questions_dict)),
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
        fallbacks=[CommandHandler('reset_score', partial(reset_score, redis_db=redis_db)),
                   CommandHandler('delete_user', partial(delete_user, redis_db=redis_db))])

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

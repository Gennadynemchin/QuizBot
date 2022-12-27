import logging
import vk_api as vk
import os
import random
import redis
import json
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from questions import check_user_answer, delete_user, reset_user_score

logger = logging.getLogger(__name__)
messenger = 'vk'


def create_user(user, messenger, redis_db):
    key = f'user_{messenger}_{user}'
    value = json.dumps({"question": None,
                        "answer": None,
                        "correct_answers": 0,
                        "total_answers": 0}, ensure_ascii=False)
    redis_db.set(key, value)


def save_new_question(user, messenger, question, answer, redis_db):
    key = f'user_{messenger}_{user}'
    user_info = json.loads(redis_db.get(key))
    correct_answers = user_info['correct_answers']
    total_answers = user_info['total_answers']
    value = json.dumps({"question": question,
                        "answer": answer,
                        "correct_answers": correct_answers,
                        "total_answers": total_answers}, ensure_ascii=False)
    redis_db.set(key, value)


def give_up(user, messenger, redis_db):
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
    return answer


def quiz_bot(vk_longpoll, vk_api, redis_db, questions_dict, keyboard):
    for event in vk_longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user = event.user_id
            if not redis_db.exists(f'user_{messenger}_{user}'):
                create_user(user, messenger, redis_db)
            if event.text == 'Новый вопрос':
                question, answer = random.choice(list(questions_dict.items()))
                save_new_question(user, messenger, question, answer, redis_db)
                vk_api.messages.send(user_id=user,
                                     message=question,
                                     random_id=0,
                                     keyboard=keyboard.get_keyboard())
            elif event.text == 'Сдаться':
                message = give_up(user, messenger, redis_db)
                if message is None:
                    message = 'Пожалуйста, нажмите "Новый вопрос"'
                vk_api.messages.send(user_id=user,
                                     message=message,
                                     random_id=0,
                                     keyboard=keyboard.get_keyboard())
            elif event.text == 'Показать результаты':
                key = f'user_{messenger}_{user}'
                user_info = json.loads(redis_db.get(key))
                correct_answers = user_info['correct_answers']
                total_answers = user_info['total_answers']
                vk_api.messages.send(user_id=user,
                                     message=f'Верных ответов: {correct_answers}\nВсего ответов: {total_answers}',
                                     random_id=0,
                                     keyboard=keyboard.get_keyboard())
            elif event.text == '/delete_user':
                key = f'user_{messenger}_{user}'
                redis_db.delete(key)
            elif event.text == '/reset_score':
                reset_user_score(redis_db, messenger, user)
            else:
                try:
                    user_answer = event.text.lower()
                    result, user_redis, user_redis_info = check_user_answer(redis_db, messenger, user, user_answer)
                    if result:
                        redis_db.set(user_redis, user_redis_info)
                        vk_api.messages.send(user_id=user,
                                             message=f"{user_answer} 'Абсолютно верно!'",
                                             random_id=0,
                                             keyboard=keyboard.get_keyboard())
                    else:
                        redis_db.set(user_redis, user_redis_info)
                        vk_api.messages.send(user_id=user,
                                             message=f"{user_answer} 'Это неправильный ответ. Попробуй еще раз'",
                                             random_id=0,
                                             keyboard=keyboard.get_keyboard())
                except AttributeError:
                    vk_api.messages.send(user_id=user,
                                         message='Я не совсем понял, что ты имеешь ввиду. '
                                                 'Попробуй нажать "Новый вопрос"',
                                         random_id=0,
                                         keyboard=keyboard.get_keyboard())


def main():
    load_dotenv()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
    vk_token = os.getenv('VK_TOKEN')
    redis_login = os.getenv('REDIS_LOGIN')
    redis_password = os.getenv('REDIS_PASSWORD')
    redis_host = os.getenv('REDIS_HOST')
    questions_path = os.getenv('QUESTIONS_PATH')

    with open(questions_path, 'r') as openfile:
        questions_dict = json.load(openfile)

    redis_db = redis.Redis(host=redis_host,
                           port=14083,
                           username=redis_login,
                           password=redis_password,
                           decode_responses=True)

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    vk_longpoll = VkLongPoll(vk_session)

    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Показать результаты', color=VkKeyboardColor.POSITIVE)

    quiz_bot(vk_longpoll, vk_api, redis_db, questions_dict, keyboard)


if __name__ == "__main__":
    main()

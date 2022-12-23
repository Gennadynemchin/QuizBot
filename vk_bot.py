import vk_api as vk
import os
import redis
import json
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.exceptions import ApiError
from questions import get_random_question, check_user_answer, delete_user, reset_user_score, questions

messenger = 'vk'


def quiz_bot(vk_longpoll, vk_api, redis_db):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Показать результаты', color=VkKeyboardColor.SECONDARY)

    for event in vk_longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user = event.user_id
            if not redis_db.exists(f'user_{messenger}_{user}'):
                # create_new_user(redis_db, 'vk', user)
                key = f'user_{messenger}_{user}'
                value = json.dumps({"question": None,
                                    "answer": None,
                                    "correct_answers": 0,
                                    "total_answers": 0}, ensure_ascii=False)
                redis_db.set(key, value)
            if event.text == 'Новый вопрос':
                question, answer = get_random_question(questions)
                key = f'user_{messenger}_{user}'
                user_info = json.loads(redis_db.get(key))
                correct_answers = user_info['correct_answers']
                total_answers = user_info['total_answers']
                value = json.dumps({"question": question,
                                    "answer": answer,
                                    "correct_answers": correct_answers,
                                    "total_answers": total_answers}, ensure_ascii=False)
                redis_db.set(key, value)
                # save_user_question(redis_db, messenger, user, question, answer)
                vk_api.messages.send(user_id=user,
                                     message=question,
                                     random_id=0,
                                     keyboard=keyboard.get_keyboard())
            elif event.text == 'Сдаться':
                try:
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
                    # message = giveup_user(redis_db, messenger, user)
                    vk_api.messages.send(user_id=user,
                                         message=answer,
                                         random_id=0,
                                         keyboard=keyboard.get_keyboard())
                except ApiError:
                    vk_api.messages.send(user_id=user,
                                         message='Попробуй нажать "Новый вопрос"',
                                         random_id=0,
                                         keyboard=keyboard.get_keyboard())
            elif event.text == 'Показать результаты':
                key = f'user_{messenger}_{user}'
                user_info = json.loads(redis_db.get(key))
                correct_answers = user_info['correct_answers']
                total_answers = user_info['total_answers']
                # correct_answers, total_answers = get_user_info(redis_db, messenger, user)
                vk_api.messages.send(user_id=user,
                                     message=f'Верных ответов: {correct_answers}\nВсего ответов: {total_answers}',
                                     random_id=0,
                                     keyboard=keyboard.get_keyboard())
            elif event.text == '/delete_user':
                delete_user(redis_db, messenger, user)
            elif event.text == '/reset_score':
                reset_user_score(redis_db, messenger, user)
            else:
                try:
                    user_answer = event.text.lower()
                    result = check_user_answer(redis_db, messenger, user, user_answer)
                    if result:
                        vk_api.messages.send(user_id=user,
                                             message=f"{user_answer} 'Абсолютно верно!'",
                                             random_id=0,
                                             keyboard=keyboard.get_keyboard())
                    else:
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
    vk_token = os.getenv('VK_TOKEN')
    redis_login = os.getenv('REDIS_LOGIN')
    redis_password = os.getenv('REDIS_PASSWORD')
    redis_host = os.getenv('REDIS_HOST')
    redis_db = redis.Redis(host=redis_host,
                           port=14083,
                           username=redis_login,
                           password=redis_password,
                           decode_responses=True)

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    vk_longpoll = VkLongPoll(vk_session)
    quiz_bot(vk_longpoll, vk_api, redis_db)


if __name__ == "__main__":
    main()

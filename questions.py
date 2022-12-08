import os
import json
import random
import redis
from dotenv import load_dotenv


def get_random_question():
    with open('sample.json', 'r') as openfile:
        json_object = json.load(openfile)
    random_question, random_answer = random.choice(list(json_object.items()))
    return [random_question, random_answer]


def create_new_user(redis_connect, messenger, user):
    key = f'user_{messenger}_{user}'
    value = json.dumps({"question": None,
                        "answer": None,
                        "correct_answers": 0,
                        "total_answers": 0}, ensure_ascii=False)
    return redis_connect.set(key, value)


def get_user_info(redis_connect, messenger, user):
    key = f'user_{messenger}_{user}'
    user_info = json.loads(redis_connect.get(key))
    correct_answers = user_info['correct_answers']
    total_answers = user_info['total_answers']
    return correct_answers, total_answers


def save_user_question(redis_connect, messenger, user, question, answer):
    key = f'user_{messenger}_{user}'
    user_info = json.loads(redis_connect.get(key))
    correct_answers = user_info['correct_answers']
    total_answers = user_info['total_answers']
    value = json.dumps({"question": question,
                        "answer": answer,
                        "correct_answers": correct_answers,
                        "total_answers": total_answers}, ensure_ascii=False)
    return redis_connect.set(key, value)


def check_user_answer(redis_connect, messenger, user, user_answer):
    key = f'user_{messenger}_{user}'
    user_info = json.loads(redis_connect.get(key))
    question = user_info['question']
    answer = user_info['answer']
    correct_answers = user_info['correct_answers']
    total_answers = user_info['total_answers']
    right_answer = user_info['answer'].replace('.', '#'). \
        replace('(', '#'). \
        replace('"', ''). \
        split('#')[0].lower()
    if user_answer == right_answer:
        value = json.dumps({"question": question,
                            "answer": answer,
                            "correct_answers": correct_answers + 1,
                            "total_answers": total_answers + 1}, ensure_ascii=False)
        redis_connect.set(key, value)
        return True
    else:
        value = json.dumps({"question": question,
                            "answer": answer,
                            "correct_answers": correct_answers,
                            "total_answers": total_answers}, ensure_ascii=False)
        redis_connect.set(key, value)
        return False


def giveup_user(redis_connect, messenger, user):
    key = f'user_{messenger}_{user}'
    user_info = json.loads(redis_connect.get(key))
    question = user_info['question']
    answer = user_info['answer']
    correct_answers = user_info['correct_answers']
    total_answers = user_info['total_answers']
    value = json.dumps({"question": question,
                        "answer": answer,
                        "correct_answers": correct_answers,
                        "total_answers": total_answers + 1}, ensure_ascii=False)
    redis_connect.set(key, value)
    return answer


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


if __name__ == '__main__':
    main()

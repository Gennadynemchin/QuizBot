import json


def get_right_answer(redis_connect, messenger, user):
    key = f'user_{messenger}_{user}'
    user_info = json.loads(redis_connect.get(key))
    right_answer = user_info['answer'].replace('.', '#'). \
        replace('(', '#'). \
        replace('"', ''). \
        split('#')[0].lower().rstrip()
    return right_answer


def reset_user_score(redis_connect, messenger, user):
    key = f'user_{messenger}_{user}'
    user_info = json.loads(redis_connect.get(key))
    question = user_info['question']
    answer = user_info['answer']
    value = json.dumps({"question": question,
                        "answer": answer,
                        "correct_answers": 0,
                        "total_answers": 0}, ensure_ascii=False)
    redis_connect.set(key, value)

import json


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
        split('#')[0].lower().rstrip()
    if user_answer == right_answer:
        value = json.dumps({"question": question,
                            "answer": answer,
                            "correct_answers": correct_answers + 1,
                            "total_answers": total_answers + 1}, ensure_ascii=False)
        return True, key, value
    else:
        value = json.dumps({"question": question,
                            "answer": answer,
                            "correct_answers": correct_answers,
                            "total_answers": total_answers}, ensure_ascii=False)
        return False, key, value


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


def delete_user(redis_connect, messenger, user):
    key = f'user_{messenger}_{user}'
    redis_connect.delete(key)

import json
from questions import redis_db


with open("sample.json", "r") as question_answer:
    json_question_answer = {}
    json_object = json.load(question_answer)
    for num, (question, answer) in enumerate(json_object.items()):
        json_question_answer[f'question_{num}'] = {"question": {question}, "answer": {answer}}

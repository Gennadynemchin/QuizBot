import os
import re
import json
from dotenv import load_dotenv


def get_questions(folder='quiz-questions'):
    questions = []
    for filename in os.listdir(folder):
        with open(os.path.join(folder, filename), 'r', encoding='koi8-r') as text:
            line = text.read()
            question_blocks = line.split('\n\n')
        for question_block in question_blocks:
            questions.append(question_block)
    return questions


def save_questions(array, filepath):
    questions = {}
    for element in array:
        if element.startswith(("Вопрос", "\nВопрос")):
            question = re.sub(" +", " ", element.split(":\n")[1].replace('\n', ' '))
        elif element.startswith(("Ответ", "\nОтвет")):
            answer = re.sub(" +", " ", element.split(":\n")[1].replace('\n', ' '))
            questions[question] = answer
    questions_answers = json.dumps(questions, indent=4, ensure_ascii=False)
    with open(filepath, "w") as outfile:
        return outfile.write(questions_answers)


def main():
    load_dotenv()
    folder_path = os.getenv('FOLDER_PATH')
    filepath = os.getenv('QUESTIONS_PATH')
    questions_answers_array = get_questions(folder_path)
    save_questions(questions_answers_array, filepath)


if __name__ == "__main__":
    main()

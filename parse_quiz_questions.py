import os
import re
import json
from dotenv import load_dotenv


def file_to_array(folder='quiz-questions'):
    array = []
    for filename in os.listdir(folder):
        with open(os.path.join(folder, filename), 'r', encoding='koi8-r') as text:
            line = text.read()
            splitter = line.split('\n\n')
        for x in splitter:
            array.append(x)
    return array


def array_to_json(array):
    dictionary = {}
    for element in array:
        if element.startswith(("Вопрос", "\nВопрос")):
            question = re.sub(" +", " ", element.split(":\n")[1].replace('\n', ' '))
        elif element.startswith(("Ответ", "\nОтвет")):
            answer = re.sub(" +", " ", element.split(":\n")[1].replace('\n', ' '))
        try:
            dictionary[question] = answer
        except Exception:
            continue
    questions_answers = json.dumps(dictionary, indent=4, ensure_ascii=False)
    with open("sample.json", "w") as outfile:
        return outfile.write(questions_answers)


def main():
    load_dotenv()
    folder_path = os.getenv('FOLDER_PATH')
    questions_answers_array = file_to_array(folder_path)
    array_to_json(questions_answers_array)


if __name__ == "__main__":
    main()

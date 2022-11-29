import os
import json


array = []
folder = 'quiz-questions'
for filename in os.listdir(folder):
    with open(os.path.join(folder, filename), 'r', encoding='koi8-r') as text:
        line = text.read()
        splitter = line.split('\n\n')
    for x in splitter:
        array.append(x)


dictionary = {}
for element in array:
    if element.startswith(("Вопрос", "\nВопрос")):
        temp_question = element.split(":\n")
        question = element.split(":\n")[1]
        question = question.replace('\n', ' ')
    elif element.startswith(("Ответ", "\nОтвет")):
        answer = element.split(":\n")[1]
        answer = answer.replace('\n', ' ')
    try:
        dictionary[question] = answer
    except Exception:
        continue

json_object = json.dumps(dictionary, indent=4, ensure_ascii=False)
print(dictionary)
with open("sample.json", "w") as outfile:
    outfile.write(json_object)


def main():
    pass


if __name__ == '__main__':
    main()

import json
import random


def get_random_question():
    with open('sample.json', 'r') as openfile:
        json_object = json.load(openfile)
    random_question, random_answer = random.choice(list(json_object.items()))
    return [random_question, random_answer]





def main():
    get_random_question()


if __name__ == '__main__':
    main()

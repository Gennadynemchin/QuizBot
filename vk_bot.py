import vk_api as vk
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from questions import vk_token, \
    get_random_question, \
    save_user_question, \
    create_new_user, \
    check_user_answer, \
    get_user_info, \
    giveup_user, \
    redis_login, \
    redis_password, \
    redis_host, \
    redis_db


messenger = 'vk'

def quiz_bot(vk_longpoll, vk_api):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Показать результаты', color=VkKeyboardColor.SECONDARY)

    for event in vk_longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user = event.user_id
            create_new_user(redis_db, 'vk', user)
            if event.text == 'Новый вопрос':
                question, answer = get_random_question()
                save_user_question(redis_db, messenger, user, question, answer)
                vk_api.messages.send(user_id=user,
                                     message=question,
                                     random_id=0,
                                     keyboard=keyboard.get_keyboard())
                else:
                    user_answer = event.text.lower()
                    result = check_user_answer(redis_db, messenger, user, user_answer)
                    if result:
                        print(f"{user_answer} 'Абсолютно верно!'")
                    else:
                        print(f"{user_answer} 'Это неправильный ответ. Попробуй еще раз'")
            elif event.text == 'Сдаться':
                message = giveup_user(redis_db, messenger, user)
                print(message)
                vk_api.messages.send(user_id=user,
                                     message=message,
                                     random_id=0,
                                     keyboard=keyboard.get_keyboard())
            elif event.text == 'Показать результаты':
                correct_answers, total_answers = get_user_info(redis_db, messenger, user)
                vk_api.messages.send(user_id=user,
                                     message=f'Верных ответов: {correct_answers}\nВсего ответов: {total_answers}',
                                     random_id=0,
                                     keyboard=keyboard.get_keyboard())




if __name__ == "__main__":
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    vk_longpoll = VkLongPoll(vk_session)
    quiz_bot(vk_longpoll, vk_api)

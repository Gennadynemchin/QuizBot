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
    redis_host


def quiz_bot(vk_longpoll, vk_api):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Показать результаты', color=VkKeyboardColor.SECONDARY)

    for event in vk_longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                vk_api.messages.send(user_id=event.user_id,
                                     message='NEW QUESTION',
                                     random_id=0,
                                     keyboard=keyboard.get_keyboard())
            elif event.text == 'Сдаться':
                vk_api.messages.send(user_id=event.user_id,
                                     message='GIVE UP',
                                     random_id=0,
                                     keyboard=keyboard.get_keyboard())
            elif event.text == 'Показать результаты':
                vk_api.messages.send(user_id=event.user_id,
                                     message='SHOW RESULTS',
                                     random_id=0,
                                     keyboard=keyboard.get_keyboard())


if __name__ == "__main__":
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    vk_longpoll = VkLongPoll(vk_session)
    quiz_bot(vk_longpoll, vk_api)

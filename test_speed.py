from pymodm import connect
from multiprocessing import Process
import datetime
import time
import sys
import pytz
from unittest import mock

from db import push_user_feeling, push_user_focus, push_user_schedule, get_user_feelings, \
    set_user_ready_flag, set_schedule_asked_today, init_user, get_schedule_by_user, auth_in_db, set_last_usage, \
    get_users_not_answer_last24hours, get_users_not_finish_survey, User
from keyboard import daily_schedule_keyboard, mood_keyboard, focus_keyboard, ready_keyboard, \
    menu_kyeboard, VALUES
from script_engine import Engine


def start(user):
    # user = init_user(user)
    set_last_usage(user)
    date = pytz.utc.localize(datetime.datetime.utcnow())
    return date


def ask_focus() -> None:
    # update.effective_user.send_message(
    #     'Подведение итогов дня поможет исследовать определенные сложности и паттерны твоего поведения. '
    #     'Каждую неделю можно выбирать разные фокусы или один и тот же. Выбрать фокус этой недели:',
    #     reply_markup=focus_keyboard())
    pass


@mock.patch('telegram.User')
@mock.patch('telegram.ext.CallbackContext')
@mock.patch('telegram.Update')
def engine_callback(user, MockUpdate, MockCallbackContext, MockUser, message=None,):
    # print(message)
    update = MockUpdate()
    update.effective_user = MockUser()
    # update.effective_user = user
    update.effective_user.id = user.id
    update.effective_user.first_name = user.first_name
    update.effective_user.username = user.username
    update.effective_user.is_bot = user.is_bot
    update.effective_user.language_code = user.language_code
    update.message.text = 'Hello'
    update.message.date = pytz.utc.localize(datetime.datetime.utcnow())
    update.effective_user.send_message.return_value = []
    if message is not None:
        update.callback_query.answer.return_value = []
        update.callback_query.data = message
        update.callback_query.message.date = pytz.utc.localize(datetime.datetime.utcnow())
    context = MockCallbackContext()
    engine = Engine(update, context)
    current_step = engine.get_next_step()
    # print(current_step.step_info)
    current_step.execute()
    return pytz.utc.localize(datetime.datetime.utcnow())


def button(user, message):
    user = init_user(user)
    set_last_usage(user)

    if message.startswith('s_'):
        text = f'Ты выбрал  в качестве времени для рассылки. Спасибо!'
        ask_focus()
        push_user_schedule(user, message, None)
    elif message.startswith('f_'):
        set_user_ready_flag(user, True)
        push_user_focus(user, message, pytz.utc.localize(datetime.datetime.utcnow()))
        return engine_callback(user)
    elif message.startswith('r_'):
        if message == 'r_yes':
            return engine_callback(user)

    elif message.startswith('m_'):
        # User entered mood
        set_user_ready_flag(user, True)
        text = f'Ты указал итогом дня . Спасибо!'
        push_user_feeling(user, message, pytz.utc.localize(datetime.datetime.utcnow()))

    return pytz.utc.localize(datetime.datetime.utcnow())


def resume_survey(user) -> None:
    # updater.bot.send_message(user, "Продолжить прохождение опроса?", reply_markup=ready_keyboard())
    pass


def dialog(id, first_name, username):
    connect('mongodb://127.0.0.1:27017/phsycho_bot_speed_test')
    user = init_user(
        User(**{'id': id, 'first_name': first_name, 'username': username, 'is_bot': False, 'language_code': 'en'}))
    time1 = pytz.utc.localize(datetime.datetime.utcnow())
    time2 = start(user)
    print(time2 - time1)

    time1 = pytz.utc.localize(datetime.datetime.utcnow())
    time2 = button(user, 's_18')
    print(time2 - time1)

    time1 = pytz.utc.localize(datetime.datetime.utcnow())
    time2 = button(user, 'f_tired')
    print(time2 - time1)

    time1 = pytz.utc.localize(datetime.datetime.utcnow())
    time2 = engine_callback(user, message='Films')
    print(time2 - time1)

    resume_survey(user)
    time1 = pytz.utc.localize(datetime.datetime.utcnow())
    time2 = button(user, 'r_yes')
    print(time2 - time1)

    time1 = pytz.utc.localize(datetime.datetime.utcnow())
    time2 = engine_callback(user, message='10')
    print(time2 - time1)

    # time1 = pytz.utc.localize(datetime.datetime.utcnow())
    # time2 = engine_callback(user, message='With hard work')
    # print(time2 - time1)


if __name__ == "__main__":
    connect('mongodb://127.0.0.1:27017/phsycho_bot_speed_test')
    users_number = int(sys.argv[1])
    first_name = 'Name'
    username = 'name'
    procs = []

    for i in range(0, users_number):
        proc = Process(target=dialog, args=(i, first_name + str(i), username + str(i)))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

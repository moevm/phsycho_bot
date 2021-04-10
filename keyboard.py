from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import VALUES, Mood, Focus
from db import TIME_VALUES


def init_button(key) -> InlineKeyboardButton:
    if key in TIME_VALUES:
        return InlineKeyboardButton(TIME_VALUES[key]['caption'], callback_data=key)
    elif key in VALUES:
        return InlineKeyboardButton(VALUES[key]['caption'], callback_data=key)
    else:
        if type(key) == Mood:
            return InlineKeyboardButton(key.value, callback_data=key.name)
        elif type(key) == Focus:
            return InlineKeyboardButton(key.value, callback_data=key.name)
        else:
            raise Exception(f'Unknown key: {key}')


def ready_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            init_button('r_yes'),
            init_button('r_1h')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def daily_schedule_keyboard() -> InlineKeyboardMarkup:
    keyboard = []
    for i in range(24):
        keyboard.append([init_button(f's_{i}')])
    keyboard.append([init_button('s_right_now')])
    return InlineKeyboardMarkup(keyboard)


def mood_keyboard() -> InlineKeyboardMarkup:
    keyboard = []
    for mood in Mood:
        keyboard.append([init_button(mood)])
    # keyboard = [
    #     [init_button('m_fun'), init_button('m_sad')],
    #     [init_button('m_angry'), init_button('m_anxious')],
    #     [init_button('m_urgent')],
    # ]

    return InlineKeyboardMarkup(keyboard)


def focus_keyboard() -> InlineKeyboardMarkup:
    keyboard = []
    for focus in Focus:
        keyboard.append([init_button(focus)])
    # keyboard = [
    #     [init_button('f_tired')],
    #     [init_button('f_self-doubt')],
    #     [init_button('f_bad')],
    #     [init_button('f_lonely')],
    #     [init_button('f_apathy')],
    #     [init_button('f_results')],
    #     [init_button('f_groundhog')]
    #
    # ]
    return InlineKeyboardMarkup(keyboard)

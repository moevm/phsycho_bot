from telegram import InlineKeyboardButton, InlineKeyboardMarkup

VALUES = {
    's_18': "18:00 - 19:00",
    's_19': "19:00 - 20:00",
    's_20': "20:00 - 21:00",

    'm_fun': "Веселый",
    'm_sad': "Грустный",
    'm_angry': "Злой",
    'm_anxious': "Тревожный",
    'm_urgent': "Состояние из ряда вон",

    'f_tired': "Усталость",
    'f_self-doubt': "Неуверенность в себе",
    'f_bad': "Все плохо",
    'f_lonely': "Одиноко",
    'f_apathy': "Апатия",
    'f_results': "Обычные итоги",
    'f_groundhog': "День сурка",

    'r_yes': 'Да',
    'r_1h': 'Ответить через час'
}


def init_button(key) -> InlineKeyboardButton:
    return InlineKeyboardButton(VALUES[key], callback_data=key)


def ready_keyboard() -> None:
    keyboard = [
        [init_button('r_yes'), init_button('r_1h')]
    ]
    return InlineKeyboardMarkup(keyboard)


def daily_schedule_keyboard() -> None:
    keyboard = [
        [init_button('s_18')], [init_button('s_19')], [init_button('s_20')]
    ]
    return InlineKeyboardMarkup(keyboard)


def mood_keyboard() -> None:
    keyboard = [
        [init_button('m_fun'), init_button('m_sad')],
        [init_button('m_angry'), init_button('m_anxious')],
        [init_button('m_urgent')], ]

    return InlineKeyboardMarkup(keyboard)


def focus_keyboard() -> None:
    keyboard = [
        [init_button('f_tired')],
        [init_button('f_self-doubt')],
        [init_button('f_bad')],
        [init_button('f_lonely')],
        [init_button('f_apathy')],
        [init_button('f_results')],
        [init_button('f_groundhog')]

    ]
    return InlineKeyboardMarkup(keyboard)

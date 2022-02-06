from telegram import InlineKeyboardButton, InlineKeyboardMarkup

VALUES = {
    's_18': "18:00 - 19:00",
    's_19': "19:00 - 20:00",
    's_20': "20:00 - 21:00",
    's_21': "21:00 - 22:00",
    's_22': "22:00 - 23:00",
    's_23': "23:00 - 24:00",
    's_right_now': "Прямо сейчас",

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

    'r_yes': "Да",
    'r_no': "Нет",
    'r_1h': "Ответить через час",
    
    'menu_change_focus': "Сменить фокус",
    'menu_share_event': "Поделиться событием",
    'menu_help': "Справка"
}


def init_button(key) -> InlineKeyboardButton:
    return InlineKeyboardButton(VALUES[key], callback_data=key)


def ready_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [init_button('r_yes'), init_button('r_1h')]
    ]
    return InlineKeyboardMarkup(keyboard)


def daily_schedule_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [init_button('s_18')],
        [init_button('s_19')],
        [init_button('s_20')],
        [init_button('s_21')],
        [init_button('s_22')],
        [init_button('s_23')],
        [init_button('s_right_now')]
    ]
    return InlineKeyboardMarkup(keyboard)


def mood_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [init_button('m_fun'), init_button('m_sad')],
        [init_button('m_angry'), init_button('m_anxious')],
        [init_button('m_urgent')], ]

    return InlineKeyboardMarkup(keyboard)


def focus_keyboard() -> InlineKeyboardMarkup:
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


def yes_no_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [init_button('r_yes')],
        [init_button('r_no')]
    ]
    return InlineKeyboardMarkup(keyboard)


def menu_kyeboard() -> InlineKeyboardMarkup:
    keyboard = [
        [init_button('menu_share_event')],
        [init_button('menu_change_focus')],
        [init_button('menu_help')]
    ]
    return InlineKeyboardMarkup(keyboard)
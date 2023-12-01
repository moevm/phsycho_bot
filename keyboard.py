from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

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
    'menu_help': "Справка",
    'change_pronoun': "Изменить обращение",
    'change_mode': "Изменить режим общения",
    'p_u': "Ты",
    'p_you': "Вы",
    'c_text': "Текстовый режим",
    'c_voice': "Голосовой режим",
    'q_1': "Где можно прочитать подробнее о методах?",
    'q_2': "Когда можно ощутить эффект от занятий?",
    'q_3': "Сколько времени потребуется уделять?",
    'q_4': "Как узнать, подходит ли мне работа с этим ботом , какие есть противопоказания?",
    'q_5': "Другой вопрос (ответит психолог-консультант)",
    'q_6': "У меня нет вопросов, хочу начать",
}


def init_button(key) -> InlineKeyboardButton:
    return InlineKeyboardButton(VALUES[key], callback_data=key)


def ready_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[init_button('r_yes'), init_button('r_1h')]]
    return InlineKeyboardMarkup(keyboard)


def daily_schedule_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [init_button('s_18')],
        [init_button('s_19')],
        [init_button('s_20')],
        [init_button('s_21')],
        [init_button('s_22')],
        [init_button('s_23')],
        [init_button('s_right_now')],
    ]
    return InlineKeyboardMarkup(keyboard)


def mood_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [init_button('m_fun'), init_button('m_sad')],
        [init_button('m_angry'), init_button('m_anxious')],
        [init_button('m_urgent')],
    ]

    return InlineKeyboardMarkup(keyboard)


def focus_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [init_button('f_tired')],
        [init_button('f_self-doubt')],
        [init_button('f_bad')],
        [init_button('f_lonely')],
        [init_button('f_apathy')],
        [init_button('f_results')],
        [init_button('f_groundhog')],
    ]
    return InlineKeyboardMarkup(keyboard)


def yes_no_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[init_button('r_yes')], [init_button('r_no')]]
    return InlineKeyboardMarkup(keyboard)


def menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [[VALUES['menu_share_event']], [VALUES['menu_change_focus']], [VALUES['menu_help']],
                [VALUES['change_pronoun']], [VALUES['change_mode']]]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def pronoun_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [init_button('p_u')],
        [init_button('p_you')],
    ]
    return InlineKeyboardMarkup(keyboard)

def conversation_mode_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [init_button('c_text')],
        [init_button('c_voice')],
    ]
    return InlineKeyboardMarkup(keyboard)

def questions_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [init_button('q_1')],
        [init_button('q_2')],
        [init_button('q_3')],
        [init_button('q_4')],
        [init_button('q_5')],
        [init_button('q_6')],
    ]
    return InlineKeyboardMarkup(keyboard)

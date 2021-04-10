from enum import Enum


VALUES = {
    'r_yes': {'caption': 'Да'},
    'r_1h': {'caption': 'Ответить через час'}
}


class Mood(Enum):
    m_fun = "Веселый"
    m_sad = "Грустный"
    m_angry = "Злой"
    m_anxious = "Тревожный"
    m_urgent = "Состояние из ряда вон"


class Focus(Enum):
    f_tired = "Усталость"
    f_self_doubt = "Неуверенность в себе"
    f_bad = "Все плохо"
    f_lonely = "Одиноко"
    f_apathy = "Апатия"
    f_results = "Обычные итоги"
    f_groundhog = "День сурка"

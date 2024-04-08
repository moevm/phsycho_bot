import gettext

from databases.db import (
    get_user_pronoun
)


def set_translation(user):
    pronoun = get_user_pronoun(user)
    languages = 'ru_official' if pronoun else 'ru'

    current_translation = gettext.translation('messages', localedir='locale', languages=[languages])
    current_translation.install()
    return current_translation

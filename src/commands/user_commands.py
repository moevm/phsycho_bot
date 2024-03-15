from telegram import Update
from telegram.ext import (
    CallbackContext
)

from src.utilities import (
    set_translation,
    dialog
)

from src.databases.db import (
    init_user,
    set_last_usage,
    get_users_not_answer_last24hours,
    get_user_feelings,
    get_users_not_finish_survey,
    change_user_pronoun,
    get_user_pronoun,
    change_user_mode,
    get_user_mode
)

from src.keyboard import (
    menu_keyboard,
    focus_keyboard
)


# def start(update: Update, context: CallbackContext) -> int:
def start(update: Update, context: CallbackContext) -> str:
    """Send a message when the command /start is issued."""

    user = init_user(update.effective_user)
    set_last_usage(user)

    translation = set_translation(user)

    dialog(
        update,
        text=translation.gettext('Здравствуйте! Я бот-психолог. Как можно обращаться к вам?'),
        reply_markup=menu_keyboard()
    )


def help_bot(update: Update, context: CallbackContext) -> None:
    user = init_user(update.effective_user)
    set_last_usage(user)
    # TODO сделать справку
    update.message.reply_text('Help!')


def stats(update: Update, context: CallbackContext) -> None:
    user = init_user(update.effective_user)
    set_last_usage(user)
    update.message.reply_text(get_user_feelings(update.effective_user))


def change_focus(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    set_last_usage(user)
    translation = set_translation(user)
    dialog(
        update,
        text=translation.gettext('Выбери новый фокус:'),
        reply_markup=focus_keyboard()
    )


def change_mode(update: Update, context: CallbackContext):
    change_user_mode(update.effective_user)
    mode = get_user_mode(update.effective_user)
    update.message.reply_text(
        f'Режим общения изменен. Текущий режим: {"текстовые сообщения" if not mode else "голосовые сообщения"}'
    )


def change_pronoun(update: Update, context: CallbackContext):
    change_user_pronoun(update.effective_user)
    pronoun = get_user_pronoun(update.effective_user)
    if pronoun:
        update.message.reply_text(
            'Режим общения изменен. Текущий режим: общение на "Вы"'
        )
    else:
        update.message.reply_text(
            'Режим общения изменен. Текущий режим: общение на "Ты"'
        )


def debug_get_users_not_finish_survey(update: Update, context: CallbackContext):
    update.message.reply_text('\n'.join(str(item) for item in get_users_not_finish_survey()))


def debug_get_users_not_answer_last24hours(update: Update, context: CallbackContext):
    update.message.reply_text('\n'.join(str(item) for item in get_users_not_answer_last24hours()))

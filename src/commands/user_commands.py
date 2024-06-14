from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)

from utilities import (
    set_translation,
    dialog
)

from databases.db import (
    init_user,
    set_last_usage,
    get_user_feelings,
    change_user_pronoun,
    get_user_pronoun,
    change_user_mode,
    get_user_mode,
    update_info
)

from databases.questions_db import (
    init_question
)

from keyboard import (
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
    dialog(
        update,
        text=f'Режим общения изменен. Текущий режим: {"текстовые сообщения" if not mode else "голосовые сообщения"}'
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


def update_user_info(update: Update, context: CallbackContext) -> None:
    update_info(update.effective_user)
    set_last_usage(update.effective_user)
    update.message.reply_text("Информация успешно обновлена.")


def start_question_conversation(update: Update, context: CallbackContext):
    update.message.reply_text("Введите вопрос:")
    user = init_user(update.effective_user)
    set_last_usage(user)
    return "add_question"


def add_question(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)

    text = update.message.text
    if len(text):
        init_question(user, text)
        update.message.reply_text("Вопрос успешно создан!")
    else:
        update.message.reply_text("Некорректно задан вопрос.")
    return ConversationHandler.END


def error_input_question(update: Update, context: CallbackContext):
    update.message.reply_text("Ожидался текст.")
    return ConversationHandler.END

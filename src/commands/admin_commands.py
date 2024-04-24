from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    Updater
)

from math import ceil

from databases.db import (
    get_users_not_answer_last24hours,
    get_users_not_finish_survey,
    init_user,
    set_last_usage,
    create_admin
)

from databases.questions_db import (
    Question,
    get_question,
    select_question,
    unselect_question,
    get_selected,
    list_questions,
    to_str_question,
    init_answer,
    get_answer,
    to_str_answer
)

from env_config import TELEGRAM_TOKEN


def debug_get_users_not_finish_survey(update: Update, context: CallbackContext):
    update.message.reply_text('\n'.join(str(item) for item in get_users_not_finish_survey()))


def debug_get_users_not_answer_last24hours(update: Update, context: CallbackContext):
    update.message.reply_text('\n'.join(str(item) for item in get_users_not_answer_last24hours()))


def add_admin(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    if not user.is_admin:
        return

    if not context.args:
        update.message.reply_text("Не введён id пользователя!")
        return

    set_last_usage(update.effective_user)
    db_id = context.args[0]

    if not (db_id.isdigit() and 6 <= len(db_id) <= 10):
        update.message.reply_text("Некорректно введён id пользователя!")
        return

    create_admin(int(db_id))
    update.message.reply_text(f"Выданы права администратора пользователю с id: {db_id}")


def get_support_questions(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    if not user.is_admin:
        return

    questions = list_questions()
    count_questions = len(questions)
    pages = ceil(count_questions / 10)

    update.message.reply_text(f"Всего страниц: {pages}.")
    set_last_usage(update.effective_user)

    if not pages:
        return

    if len(context.args) and context.args[0].isdigit():
        out_page_number = int(context.args[0])

        if out_page_number > pages:
            out_page_number = 1
    else:
        out_page_number = 1

    page_questions = questions[(out_page_number - 1) * 10: out_page_number * 10 - 1]
    out_questions = '\n\n'.join([to_str_question(elem) for elem in page_questions])
    update.message.reply_text(out_questions)


def get_answer_with_id(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    if not user.is_admin:
        return

    if len(context.args):
        answer_id = context.args[0]
    else:
        update.message.reply_text("Произошла ошибка.")
        return

    answer = get_answer(answer_id)
    if not answer:
        return
    update.message.reply_text(to_str_answer(answer))


def answer_support_question(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)

    if not user.is_admin:
        return ConversationHandler.END

    update.message.reply_text("Введите идентификатор вопроса:")

    set_last_usage(user)
    return "get_answer_id"


def get_answer_id(update: Update, context: CallbackContext):
    text = update.message.text
    question = get_question(text)
    if not question:
        update.message.reply_text("Произошла ошибка. Не существует вопроса с таким идентификатором.")
        return ConversationHandler.END

    user = init_user(update.effective_user)
    select_question(user.id, question)

    update.message.reply_text(f'Выбранный вопрос: "{question.text}"')
    update.message.reply_text("Введите ответ:")
    return "add_answer"


def add_answer(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    text = update.message.text

    selected_question = get_selected(user.id)
    if not selected_question:
        update.message.reply_text("Произошла ошибка. Где-то утерян идентификатор для select вопроса.")
        return ConversationHandler.END

    if text:
        init_answer(selected_question.get_id(), text)
        update.message.reply_text("Ответ успешно создан!")
        send_answer_to_user(selected_question, text)
    return ConversationHandler.END


def error_input_answer(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    unselect_question(user.id)
    update.message.reply_text("Произошла ошибка.")
    return ConversationHandler.END


def send_answer_to_user(question: Question, text: str):
    to_user = question.user_id

    if not to_user:
        return

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    updater.bot.send_message(to_user, text)

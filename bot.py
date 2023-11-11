import sys
import queue
import threading
import gettext

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    Filters,
)

import my_cron
from db import (
    push_user_feeling,
    push_user_focus,
    push_user_schedule,
    get_user_feelings,
    set_user_ready_flag,
    set_schedule_asked_today,
    init_user,
    create_admin,
    update_info,
    get_schedule_by_user,
    auth_in_db,
    set_last_usage,
    get_users_not_answer_last24hours,
    get_users_not_finish_survey,
    get_user_mode,
    change_user_mode,
    get_user_word_statistics,
)

from questions_db import (
    init_question,
    list_questions,
    init_answer,
)

from keyboard import (
    daily_schedule_keyboard,
    mood_keyboard,
    focus_keyboard,
    ready_keyboard,
    menu_kyeboard,
    VALUES,
)
from env_config import DEBUG_MODE, DEBUG_ON, ADMIN

from logs import init_logger
from script_engine import Engine
from voice_module import work_with_audio
from silero_module import bot_answer_audio, clear_audio_cache
from wrapper import dialog

_ = gettext.gettext

DAYS_OFFSET = 7

PREPARE, TYPING, SELECT_YES_NO, MENU = "PREPARE", "TYPING", "SELECT_YES_NO", "MENU"


# def start(update: Update, context: CallbackContext) -> int:
def start(update: Update, context: CallbackContext) -> str:
    """Send a message when the command /start is issued."""

    user = init_user(update.effective_user)
    update_user_info(update, context)
    set_last_usage(user)

    dialog(
        update,
        text=_('Привет! Я бот, который поможет тебе отрефлексировать твое настроение'),
        reply_markup=menu_kyeboard()
    )

    dialog(
        update,
        text=_('В какое время тебе удобно подводить итоги дня?'),
        reply_markup=daily_schedule_keyboard()
    )


def ask_focus(update: Update) -> None:
    dialog(
        update,
        text=_('Подведение итогов дня поможет исследовать определенные сложности и паттерны твоего поведения. '
               'Каждую неделю можно выбирать разные фокусы или один и тот же. Выбрать фокус этой недели:'),
        reply_markup=focus_keyboard()
    )


# def button(update: Update, context: CallbackContext) -> int:
def button(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    query.answer()

    user = init_user(update.effective_user)
    set_last_usage(user)

    last_message = query.message.text

    if query.data.startswith('s_'):
        # User entered schedule
        text = _('Ты выбрал ') + VALUES[query.data] + _(' в качестве времени для рассылки. Спасибо!')

        query.delete_message()
        dialog(update, text=text)
        # query.edit_message_text(text=text)

        ask_focus(update)
        push_user_schedule(update.effective_user, query.data, update.effective_message.date)

    elif query.data.startswith('f_'):
        # User entered week focus
        set_user_ready_flag(update.effective_user, True)
        push_user_focus(update.effective_user, query.data, update.effective_message.date)

        return engine_callback(update, context)
    elif query.data.startswith('r_') and (
            last_message
            in [_('Привет! Пришло время подводить итоги. Давай?'), _('Продолжить прохождение опроса?')]
    ):
        if query.data == 'r_yes':
            return engine_callback(update, context)
        if query.data == 'r_1h':
            text = _('Понял тебя. Спрошу через час')
            query.edit_message_text(text=text)
            set_user_ready_flag(update.effective_user, True)

    elif query.data.startswith('m_'):
        # User entered mood
        set_user_ready_flag(update.effective_user, True)
        text = _('Ты указал итогом дня ') + VALUES[query.data] + _('. Спасибо!')

        query.delete_message()
        dialog(update, text=text)
        # query.edit_message_text(text=text)

        push_user_feeling(update.effective_user, query.data, update.effective_message.date)

        # debugging zone
        if DEBUG_MODE == DEBUG_ON:
            user = init_user(update.effective_user)
            schedule = get_schedule_by_user(user, is_test=True)
            print(schedule)
            if schedule:
                if len(schedule.sending_list) < DAYS_OFFSET:
                    schedule.is_on = True
                    schedule.save()

    return ''


def text_processing(update: Update, context: CallbackContext):
    if update.message.text == VALUES['menu_share_event']:
        # TODO обработка выбора "поделиться событием"
        pass
    elif update.message.text == VALUES['menu_change_focus']:
        change_focus(update, context)
    elif update.message.text == VALUES['menu_help']:
        help_bot(update, context)
    else:
        # example of using get_user_word_statistics()
        user = init_user(update.effective_user)
        answers_statistics = str(get_user_word_statistics(user.id))
        update.effective_user.send_message(answers_statistics)

        engine_callback(update, context)


def help_bot(update: Update, context: CallbackContext) -> None:
    user = init_user(update.effective_user)
    set_last_usage(user)
    # TODO сделать справку
    update.message.reply_text('Help!')


def stats(update: Update, context: CallbackContext) -> None:
    user = init_user(update.effective_user)
    set_last_usage(user)
    update.message.reply_text(get_user_feelings(update.effective_user))


def debug_get_users_not_answer_last24hours(update: Update, context: CallbackContext):
    update.message.reply_text('\n'.join(str(item) for item in get_users_not_answer_last24hours()))


def error(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Error!')


def debug_get_users_not_finish_survey(update: Update, context: CallbackContext):
    update.message.reply_text('\n'.join(str(item) for item in get_users_not_finish_survey()))


def ask_ready(updater, schedule):
    # set_schedule_is_on_flag(schedule, False)
    set_schedule_asked_today(schedule)
    updater.bot.send_message(
        schedule.user.id,
        _("Привет! Пришло время подводить итоги. Давай?"),
        reply_markup=ready_keyboard(),
    )


def resume_survey(updater, user) -> None:
    updater.bot.send_message(user, _("Продолжить прохождение опроса?"), reply_markup=ready_keyboard())


def ask_feelings(update: Update, context: CallbackContext) -> None:
    dialog(
        update,
        text=_("Расскажи, как прошел твой день?"),
        reply_markup=mood_keyboard()
    )


# def engine_callback(update, context: CallbackContext) -> int:
def engine_callback(update, context: CallbackContext) -> str:
    engine = Engine(update, context)
    current_step = engine.get_next_step()
    current_step.execute()


def cancel(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    set_last_usage(user)
    dialog(update, text=_('Всего хорошего.'))
    return ConversationHandler.END


def change_focus(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    set_last_usage(user)

    dialog(
        update,
        text=_('Выбери новый фокус:'),
        reply_markup=focus_keyboard()
    )


def send_audio_answer(update: Update, context: CallbackContext):
    update.effective_user.send_message(_("Уже обрабатываю твоё сообщение"))

    text = update.message.text  # 'Спасибо, что поделился своими переживаниями'
    audio = bot_answer_audio(text)

    if audio:
        update.effective_user.send_voice(voice=audio.content)
        # push_bot_answer(update.update_id, answer=audio.content, text=text)
        clear_audio_cache()  # only for testing
    else:
        error(update, context)


def add_admin(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    if user.is_admin:

        if len(context.args):
            db_id = context.args[0]

            if db_id.isdigit() and 6 <= len(db_id) <= 10:
                create_admin(int(db_id))
                update.message.reply_text(f"Выданы права администратора пользователю с id: {db_id}")
            else:
                update.message.reply_text("Некорректно введён id пользователя!")

            set_last_usage(update.effective_user)
        else:
            update.message.reply_text("Не введён id пользователя!")


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
        update.message.reply_text("Произошла ошибка.")
    return ConversationHandler.END


def error_input_question(update: Update, context: CallbackContext):
    update.message.reply_text("Ожидался текст.")
    return ConversationHandler.END


def update_user_info(update: Update, context: CallbackContext):
    update_info(update.effective_user)
    set_last_usage(update.effective_user)
    update.message.reply_text("Данные успешно обновлены.")


def change_mode(update: Update, context: CallbackContext):
    change_user_mode(update.effective_user)
    mode = get_user_mode(update.effective_user)
    update.message.reply_text(
        f'Режим общения изменен. Текущий режим: {"текстовые сообщения" if not mode else "голосовые сообщения"}'
    )


def main(token):
    init_logger()

    updater = Updater(token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('add_admin', add_admin))
    updater.dispatcher.add_handler(CommandHandler('update_info', update_user_info))

    updater.dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('add_question', start_question_conversation)],
            states={
                "add_question": [
                    MessageHandler(Filters.text & ~Filters.command, add_question)
                ]
            },
            fallbacks=[
                MessageHandler(Filters.voice | Filters.command, error_input_question)
            ]
        )
    )

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help_bot))
    updater.dispatcher.add_handler(CommandHandler('stats', stats))
    updater.dispatcher.add_handler(CommandHandler('change_focus', change_focus))
    updater.dispatcher.add_handler(CommandHandler('change_mode', change_mode))
    updater.dispatcher.add_handler(
        CommandHandler('get_users_not_finish_survey', debug_get_users_not_finish_survey)
    )
    updater.dispatcher.add_handler(
        CommandHandler('get_users_not_answer_last24hours', debug_get_users_not_answer_last24hours)
    )
    updater.dispatcher.add_handler(CommandHandler('cancel', cancel))

    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_processing))
    updater.dispatcher.add_handler(MessageHandler(Filters.voice, work_with_audio))

    updater.start_polling()


# updater.idle()


class Worker(threading.Thread):
    def __init__(self, tokens_queue):
        super().__init__()
        self.work_queue = tokens_queue

    def run(self):
        try:
            token_try = self.work_queue.get()
            self.process(token_try)

            # TODO переделать на получение пользователя
            if ADMIN.isdigit():
                create_admin(int(ADMIN))
        finally:

            pass

    @staticmethod
    def process(token_):
        auth_in_db(username=sys.argv[2], password=sys.argv[3])
        if token_ == 'bot':
            main(sys.argv[1])
        else:
            my_cron.main(sys.argv[1])


if __name__ == '__main__':
    tokens = ['bot', 'schedule']
    work_queue = queue.Queue()
    for token in tokens:
        work_queue.put(token)
    for i in range(len(tokens)):
        worker = Worker(work_queue)
        worker.start()

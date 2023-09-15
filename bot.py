import sys
import queue
import threading

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
    get_schedule_by_user,
    auth_in_db,
    set_last_usage,
    get_users_not_answer_last24hours,
    get_users_not_finish_survey,
    get_user_word_statistics,
)
from keyboard import (
    daily_schedule_keyboard,
    mood_keyboard,
    focus_keyboard,
    ready_keyboard,
    menu_kyeboard,
    VALUES,
)
from logs import init_logger
from script_engine import Engine
from voice_module import work_with_audio
from silero_module import bot_answer_audio, clear_audio_cache

DAYS_OFFSET = 7
DEBUG = True

PREPARE, TYPING, SELECT_YES_NO, MENU = "PREPARE", "TYPING", "SELECT_YES_NO", "MENU"


# def start(update: Update, context: CallbackContext) -> int:
def start(update: Update, context: CallbackContext) -> str:
    """Send a message when the command /start is issued."""

    user = init_user(update.effective_user)
    set_last_usage(user)

    update.message.reply_text(
        'Привет! Я бот, который поможет тебе отрефлексировать твое настроение',
        reply_markup=menu_kyeboard(),
    )
    update.message.reply_text(
        'В какое время тебе удобно подводить итоги дня?', reply_markup=daily_schedule_keyboard()
    )


def ask_focus(update: Update) -> None:
    update.effective_user.send_message(
        'Подведение итогов дня поможет исследовать определенные сложности и паттерны твоего поведения. '
        'Каждую неделю можно выбирать разные фокусы или один и тот же. Выбрать фокус этой недели:',
        reply_markup=focus_keyboard(),
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
        text = f'Ты выбрал {VALUES[query.data]} в качестве времени для рассылки. Спасибо!'
        query.edit_message_text(text=text)
        ask_focus(update)
        push_user_schedule(update.effective_user, query.data, update.effective_message.date)
    elif query.data.startswith('f_'):
        # User entered week focus
        set_user_ready_flag(update.effective_user, True)
        push_user_focus(update.effective_user, query.data, update.effective_message.date)
        return engine_callback(update, context)

    elif query.data.startswith('r_') and (
        last_message
        in ['Привет! Пришло время подводить итоги. Давай?', 'Продолжить прохождение опроса?']
    ):
        if query.data == 'r_yes':
            return engine_callback(update, context)
        if query.data == 'r_1h':
            text = 'Понял тебя. Спрошу через час'
            query.edit_message_text(text=text)
            set_user_ready_flag(update.effective_user, True)

    elif query.data.startswith('m_'):
        # User entered mood
        set_user_ready_flag(update.effective_user, True)
        text = f'Ты указал итогом дня "{VALUES[query.data]}". Спасибо!'
        query.edit_message_text(text=text)
        push_user_feeling(update.effective_user, query.data, update.effective_message.date)

        # debugging zone
        if DEBUG:
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
        user_help(update, context)
    else:
        # example of using get_user_word_statistics()
        user = init_user(update.effective_user)
        answers_statistics = str(get_user_word_statistics(user.id))
        update.effective_user.send_message(answers_statistics)

        engine_callback(update, context)


def user_help(update: Update, context: CallbackContext) -> None:
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
        "Привет! Пришло время подводить итоги. Давай?",
        reply_markup=ready_keyboard(),
    )


def resume_survey(updater, user) -> None:
    updater.bot.send_message(user, "Продолжить прохождение опроса?", reply_markup=ready_keyboard())


def ask_feelings(update: Update, context: CallbackContext) -> None:
    update.effective_user.send_message(
        "Расскажи, как прошел твой день?", reply_markup=mood_keyboard()
    )


# def engine_callback(update, context: CallbackContext) -> int:
def engine_callback(update, context: CallbackContext) -> str:
    engine = Engine(update, context)
    current_step = engine.get_next_step()
    current_step.execute()


def cancel(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    set_last_usage(user)
    update.message.reply_text('Всего хорошего.')
    return ConversationHandler.END


def change_focus(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    set_last_usage(user)
    update.effective_user.send_message('Выберете новый фокус:', reply_markup=focus_keyboard())


def send_audio_answer(update: Update, context: CallbackContext):
    update.effective_user.send_message("Уже обрабатываю твоё сообщение")

    text = update.message.text  # 'Спасибо, что поделился своими переживаниями'
    audio = bot_answer_audio(text)

    if audio:
        update.effective_user.send_voice(voice=audio.content)
        # push_bot_answer(update.update_id, answer=audio.content, text=text)
        clear_audio_cache()
    else:
        error(update, context)


def main(token, mode):
    init_logger()

    updater = Updater(token, use_context=True)
    if mode == "voice":
        updater.dispatcher.add_handler(MessageHandler(Filters.voice, work_with_audio))
        updater.dispatcher.add_handler(MessageHandler(Filters.text, send_audio_answer))

    elif mode == "text":
        updater.dispatcher.add_handler(CommandHandler('start', start))
        updater.dispatcher.add_handler(CommandHandler('user_help', user_help))
        updater.dispatcher.add_handler(CommandHandler('stats', stats))
        updater.dispatcher.add_handler(CommandHandler('change_focus', change_focus))
        updater.dispatcher.add_handler(
            CommandHandler('get_users_not_finish_survey', debug_get_users_not_finish_survey)
        )
        updater.dispatcher.add_handler(
            CommandHandler(
                'get_users_not_answer_last24hours', debug_get_users_not_answer_last24hours
            )
        )
        updater.dispatcher.add_handler(CommandHandler('cancel', cancel))

        updater.dispatcher.add_handler(CallbackQueryHandler(button))
        updater.dispatcher.add_handler(
            MessageHandler(Filters.text & ~Filters.command, text_processing)
        )
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
        finally:
            pass

    @staticmethod
    def process(token_):
        auth_in_db(username=sys.argv[2], password=sys.argv[3])
        if token_ == 'bot':
            main(sys.argv[1], sys.argv[4])
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

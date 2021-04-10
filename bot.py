import logging
import sys
import threading
import queue
import my_cron

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

from db import push_user_feeling, push_user_focus, push_user_schedule, get_user_feelings, \
    set_user_ready_flag, set_schedule_asked_today, init_user, get_schedule_by_user, auth_in_db, TIME_VALUES
from keyboard import daily_schedule_keyboard, mood_keyboard, focus_keyboard, ready_keyboard
from config import VALUES, Focus, Mood


DAYS_OFFSET = 7
DEBUG = True


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    update.message.reply_text('Привет! Я бот, который поможет тебе отрефлексировать твое настроение')
    update.message.reply_text('В какое время тебе удобно подводить итоги дня?', reply_markup=daily_schedule_keyboard())


def ask_focus(update: Update) -> None:
    update.effective_user.send_message(
        'Подведение итогов дня поможет исследовать определенные сложности и паттерны твоего поведения. '
        'Каждую неделю можно выбирать разные фокусы или один и тот же. Выбрать фокус этой недели:',
        reply_markup=focus_keyboard())


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data.startswith('s_'):
        # User entered schedule
        text = f"Ты выбрал {TIME_VALUES[query.data]['caption']} в качестве времени для рассылки. Спасибо!"
        query.edit_message_text(text=text)
        ask_focus(update)
        push_user_schedule(update.effective_user, query.data, update.effective_message.date)
    elif query.data.startswith('f_'):
        # User entered week focus
        set_user_ready_flag(update.effective_user, True)
        text = f'Ты выбрал фокусом этой недели "{Focus[query.data].value}". ' \
               f'Спасибо! В указанное тобой время я попрошу тебя рассказать, как прошел твой день'
        query.edit_message_text(text=text)
        push_user_focus(update.effective_user, query.data, update.effective_message.date)
    elif query.data.startswith('r_'):
        # User answered to feelings request
        if query.data == 'r_yes':
            ask_feelings(update)
            query.delete_message()
        else:
            text = f'Понял тебя. Спрошу через час'
            query.edit_message_text(text=text)
            set_user_ready_flag(update.effective_user, True)
    elif query.data.startswith('m_'):
        # User entered mood
        set_user_ready_flag(update.effective_user, True)
        text = f'Ты указал итогом дня "{Mood[query.data].value}". Спасибо!'
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


def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')


def stats(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(get_user_feelings(update.effective_user))


def error(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Error!')


def ask_ready(updater, schedule):
    # set_schedule_is_on_flag(schedule, False)
    set_schedule_asked_today(schedule)
    updater.bot.send_message(schedule.user.id, "Привет! Пришло время подводить итоги. Давай?",
                             reply_markup=ready_keyboard())


def ask_feelings(update):
    update.effective_user.send_message("Расскажи, как прошел твой день?", reply_markup=mood_keyboard())


def main(token):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    updater = Updater(token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('stats', stats))
    # updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    # updater.idle()


class Worker(threading.Thread):
    def __init__(self, tokens_queue):
        super(Worker, self).__init__()
        self.work_queue = tokens_queue

    def run(self):
        try:
            token_try = self.work_queue.get()
            self.process(token_try)
        finally:
            pass

    def process(self, token_):
        auth_in_db(username=sys.argv[2],
                   password=sys.argv[3])
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

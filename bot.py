import logging
import sys

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

from db import push_user_feeling, push_user_focus, push_user_schedule, get_user_feelings, \
    set_user_ready_flag, set_schedule_is_on_flag
from keyboard import daily_schedule_keyboard, mood_keyboard, focus_keyboard, ready_keyboard, VALUES


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
        text = f'Ты выбрал {VALUES[query.data]} в качестве времени для рассылки. Спасибо!'
        query.edit_message_text(text=text)
        ask_focus(update)
        push_user_schedule(update.effective_user, query.data, update.effective_message.date)
    elif query.data.startswith('f_'):
        # User entered week focus
        set_user_ready_flag(update.effective_user, True)
        text = f'Ты выбрал фокусом этой недели "{VALUES[query.data]}". ' \
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
        text = f'Ты указал итогом дня "{VALUES[query.data]}". Спасибо!'
        query.edit_message_text(text=text)
        push_user_feeling(update.effective_user, query.data, update.effective_message.date)


def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')


def stats(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(get_user_feelings(update.effective_user))


def error(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Error!')


def ask_ready(updater, schedule):
    set_schedule_is_on_flag(schedule, False)
    updater.bot.send_message(schedule.user.id, "Привет! Пришло время подводить итоги. Давай?", reply_markup=ready_keyboard())


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


if __name__ == '__main__':
    main(sys.argv[1])

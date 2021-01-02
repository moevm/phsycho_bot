from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import logging
import sys 
from db import push_user_feeling, get_user_feelings, get_user_list
import schedule
import time


def keyboard_setup() -> None:
    keyboard = [
        [
            InlineKeyboardButton("Веселый", callback_data='fun'),
            InlineKeyboardButton("Грустный", callback_data='sad'),
        ],
        [
            InlineKeyboardButton("Злой", callback_data='angry'),
            InlineKeyboardButton("Тревожный", callback_data='anxious'),
        ],
        [InlineKeyboardButton("Состояние из ряда вон", callback_data='urgent')],
        [InlineKeyboardButton("Моя статистика (также доступно по команде /stats)", callback_data='stats')]
    ]

    return InlineKeyboardMarkup(keyboard)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    update.message.reply_text('Привет! Я бот, который поможет тебе отрефлексировать твое настроение. Расскажи, как ты себя чувствуешь?', reply_markup=keyboard_setup())

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    push_user_feeling(update.effective_user.id, query.data, update.effective_message.date)

    text = "Спасибо за ответ! "
    if query.data == "urgent":
        text = "Ого!"
    if query.data == "stats":
        text = get_user_feelings(update.effective_user.id)

    query.edit_message_text(text=text)


def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')

def stats(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(get_user_feelings(update.effective_user.id))

def error(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Error!')


def cron(updater):
    users = get_user_list()
    for user in users:
        updater.bot.send_message(user, "Расскажи, как ты себя чувствуешь?", reply_markup=setup_keyboard())


def main(token):

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    updater = Updater(token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('stats', stats))
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    #updater.idle()

    schedule.every(5).minutes.do(cron, updater=updater)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main(sys.argv[1])

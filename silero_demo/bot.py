import config
import sys
import os

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

from silero_test import *
def start_callback(update: Update, context: CallbackContext) -> None:
    msg = "Отправь мне сообщение"
    update.message.reply_text(msg)

def send_audio_answer(update: Update, context: CallbackContext):
    audio = silero_test()
    with open(audio, 'rb') as f:
        update.effective_user.send_audio(f)

def main(token):
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # simple start function
    dispatcher.add_handler(CommandHandler("start", start_callback))

    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    dispatcher.add_handler(MessageHandler(Filters.voice, send_audio_answer))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main(sys.argv[1])
    # main(config.BOT_TOKEN)
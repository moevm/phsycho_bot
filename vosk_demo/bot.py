import logging
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

from audio_recognizer import VoskAudioRecognizer

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start_callback(update: Update, context: CallbackContext) -> None:
    msg = "Отправь мне голосовое сообщение)"
    print("Start!")
    update.message.reply_text(msg)


def audio_handler(update, context):
    print(update.message.audio)
    update.message.reply_text("What a nice sound!")


def voice_handler(update, context):
    update.message.voice.get_file().download()
    filename = update.message.voice.get_file().file_path
    filename = filename.split('/')[-1]
    recognizer = VoskAudioRecognizer(config.VOSK_URL)
    recognizer.recognize(filename)
    os.remove(filename)
    update.message.reply_text("Спасибо!")


def main(token):
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # simple start function
    dispatcher.add_handler(CommandHandler("start", start_callback))

    # Add message handler for audio messages
    dispatcher.add_handler(MessageHandler(Filters.audio, audio_handler))
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    dispatcher.add_handler(MessageHandler(Filters.voice, voice_handler))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main(sys.argv[1])
    # main(config.BOT_TOKEN)

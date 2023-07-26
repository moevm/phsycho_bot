import sys

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from silero_test import silero_test


def start_callback(update: Update, context: CallbackContext) -> None:
    msg = "Отправь мне сообщение"
    update.message.reply_text(msg)


def send_audio_answer_text(update: Update, context: CallbackContext):
    audio = silero_test(handle_text(update, context))
    with open(audio, 'rb') as file_:
        update.effective_user.send_audio(file_)


def send_audio_answer_voice(update: Update, context: CallbackContext):
    audio = silero_test()
    with open(audio, 'rb') as file_:
        update.effective_user.send_audio(file_)


def handle_text(update: Update, context: CallbackContext):
    message_text = update.message.text
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text='Обрабытваю сообщение...')
    return message_text


def main(token, mode):
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # simple start function
    dispatcher.add_handler(CommandHandler("start", start_callback))

    if mode == 'text':
        # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
        dispatcher.add_handler(MessageHandler(Filters.text, send_audio_answer_text))
    elif mode == 'voice':
        dispatcher.add_handler(MessageHandler(Filters.voice, send_audio_answer_voice))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
    # main(config.BOT_TOKEN)

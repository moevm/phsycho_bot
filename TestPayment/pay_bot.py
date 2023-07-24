#!/usr/bin/env python

"""
Basic example for a bot that can receive payment from user.
"""

import logging
import config

from telegram import LabeledPrice, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    PreCheckoutQueryHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start_callback(update: Update, context: CallbackContext) -> None:
    msg = "Use /buy to get an invoice for payment"
    update.message.reply_text(msg)


def start_without_shipping_callback(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    title = "Payment Example"
    description = "Payment Example using python-telegram-bot"
    # select a payload just for you to recognize its the donation from your bot
    payload = "Custom-Payload"
    # In order to get a provider_token see
    # https://core.telegram.org/bots/payments#getting-a-token
    provider_token = config.PROVIDER_TOKEN
    start_parameter = "test-payment"
    currency = "RUB"
    # min price in rub = 10
    price = 10
    # price * 100 so as to include 2 decimal points
    prices = [LabeledPrice("Test", price * 100)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    context.bot.send_invoice(chat_id, title, description, payload, provider_token, start_parameter, currency, prices)


# after (optional) shipping, it's the pre-checkout
def precheckout_callback(update: Update, context: CallbackContext) -> None:
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'Custom-Payload':
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)


# finally, after contacting the payment provider...
def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    # do something after successfully receiving payment?
    update.message.reply_text("Thank you for your payment!")


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # simple start function
    dispatcher.add_handler(CommandHandler("start", start_callback))

    # Add command handler to start the payment invoice
    dispatcher.add_handler(CommandHandler("buy", start_without_shipping_callback))

    # Pre-checkout handler to final check
    dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    # Success! Notify your user!
    dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

from telegram import Update
from telegram.ext import (
    CallbackContext
)

from databases.db import (
    get_users_not_answer_last24hours,
    get_users_not_finish_survey
)


def debug_get_users_not_finish_survey(update: Update, context: CallbackContext):
    update.message.reply_text('\n'.join(str(item) for item in get_users_not_finish_survey()))


def debug_get_users_not_answer_last24hours(update: Update, context: CallbackContext):
    update.message.reply_text('\n'.join(str(item) for item in get_users_not_answer_last24hours()))
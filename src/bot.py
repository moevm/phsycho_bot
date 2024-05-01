import sys
import queue
import threading

from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)

from databases.db import (
    auth_in_db
)

from modules.stt_module.voice_module import (
    work_with_audio
)

from commands.user_commands import (
    start,
    help_bot,
    stats,
    change_focus,
    change_mode,
    change_pronoun
)

from commands.admin_commands import (
    debug_get_users_not_answer_last24hours,
    debug_get_users_not_finish_survey
)

from commands.handlers import (
    cancel,
    button,
    text_processing
)

import my_cron
import kafka.kafka_consumer

from logs import init_logger


def main(token):
    init_logger()
    updater = Updater(token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help_bot))
    updater.dispatcher.add_handler(CommandHandler('stats', stats))
    updater.dispatcher.add_handler(CommandHandler('change_focus', change_focus))
    updater.dispatcher.add_handler(CommandHandler('change_mode', change_mode))
    updater.dispatcher.add_handler(CommandHandler('change_pronoun', change_pronoun))

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
        finally:
            pass

    @staticmethod
    def process(token_):
        auth_in_db(username=sys.argv[2], password=sys.argv[3])
        if token_ == 'bot':
            main(sys.argv[1])
        elif token_ == 'kafka':
            kafka.kafka_consumer.main()
        else:
            my_cron.main(sys.argv[1])


if __name__ == '__main__':
    tokens = ['bot', 'schedule', 'kafka']
    work_queue = queue.Queue()
    for token in tokens:
        work_queue.put(token)
    for i in range(len(tokens)):
        worker = Worker(work_queue)
        worker.start()
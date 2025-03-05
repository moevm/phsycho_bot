import sys
import queue
import threading

from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    ConversationHandler
)

from databases.db import (
    auth_in_db,
    create_admin
)

from modules.stt_module.voice_module import (
    work_with_audio
)

from modules.video.video_module import (
    work_with_video
)

from commands.user_commands import (
    start,
    help_bot,
    stats,
    change_focus,
    change_mode,
    change_pronoun,
    update_user_info,
    start_question_conversation,
    add_question,
    error_input_question
)

from commands.admin_commands import (
    debug_get_users_not_answer_last24hours,
    debug_get_users_not_finish_survey,
    add_admin,
    add_answer,
    get_support_questions,
    get_answer_with_id,
    start_answer_conversation,
    get_answer_id,
    error_input_answer
)

from commands.handlers import (
    cancel,
    button,
    text_processing
)

from env_config import ADMIN

import my_cron
import kafka.consumer_tts
import kafka.consumer_stt

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

    updater.dispatcher.add_handler(CommandHandler('add_admin', add_admin))
    updater.dispatcher.add_handler(CommandHandler('get_support_questions', get_support_questions))
    updater.dispatcher.add_handler(CommandHandler('update_info', update_user_info))
    updater.dispatcher.add_handler(CommandHandler('get_answer_with_id', get_answer_with_id))

    updater.dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('add_question', start_question_conversation)],
            states={
                "add_question": [
                    MessageHandler(Filters.text & ~Filters.command, add_question)
                ]
            },
            fallbacks=[
                MessageHandler(Filters.voice | Filters.command, error_input_question)
            ]
        )
    )

    updater.dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('answer_support_question', start_answer_conversation)],
            states={
                "get_answer_id": [
                    MessageHandler(Filters.text & ~Filters.command, get_answer_id)
                ],
                "add_answer": [
                    MessageHandler(Filters.text & ~Filters.command, add_answer)
                ]
            },
            fallbacks=[
                MessageHandler(Filters.voice | Filters.command, error_input_answer)
            ]
        )
    )

    updater.dispatcher.add_handler(CommandHandler('cancel', cancel))

    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_processing))
    updater.dispatcher.add_handler(MessageHandler(Filters.video_note, work_with_video))
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

            if ADMIN.isdigit():
                create_admin(int(ADMIN))
        finally:
            pass

    @staticmethod
    def process(token_):
        auth_in_db(username=sys.argv[2], password=sys.argv[3])
        if token_ == 'bot':
            main(sys.argv[1])
        elif token_ == 'kafka-tts':
            kafka.consumer_tts.main()
        elif token_ == 'kafka-stt':
            kafka.consumer_stt.main()
        else:
            my_cron.main(sys.argv[1])


if __name__ == '__main__':
    tokens = ['bot', 'schedule', 'kafka-tts', 'kafka-stt']
    work_queue = queue.Queue()
    for token in tokens:
        work_queue.put(token)
    for i in range(len(tokens)):
        worker = Worker(work_queue)
        worker.start()

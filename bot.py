import sys
import queue
import threading
import gettext

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    Filters,
)

import my_cron
from db import (
    push_user_feeling,
    push_user_focus,
    push_user_schedule,
    get_user_feelings,
    set_user_ready_flag,
    set_schedule_asked_today,
    init_user,
    get_schedule_by_user,
    auth_in_db,
    set_last_usage,
    get_users_not_answer_last24hours,
    get_users_not_finish_survey,
    get_user_mode,
    change_user_mode,
    push_user_chosen_name,
    push_user_pronoun,
    change_user_pronoun,
    get_user_pronoun,
    get_user_chosen_name,
    push_user_mode,
    push_user_initial_reason,
    get_user_initial_reason_flag,
    set_user_initial_reason_flag,
    get_user_word_statistics,
)
from keyboard import (
    mood_keyboard,
    focus_keyboard,
    ready_keyboard,
    VALUES,
    pronoun_keyboard,
    conversation_mode_keyboard,
    questions_keyboard,
    menu_keyboard,
    daily_schedule_keyboard,
)
from env_config import (DEBUG_MODE,
                        DEBUG_ON)

from logs import init_logger
from script_engine import Engine
from voice_module import work_with_audio
from silero_module import bot_answer_audio, clear_audio_cache
from wrapper import dialog

_ = gettext.gettext

DAYS_OFFSET = 7

PREPARE, TYPING, SELECT_YES_NO, MENU = "PREPARE", "TYPING", "SELECT_YES_NO", "MENU"


# def start(update: Update, context: CallbackContext) -> int:
def start(update: Update, context: CallbackContext) -> str:
    """Send a message when the command /start is issued."""

    user = init_user(update.effective_user)
    set_last_usage(user)

    dialog(
        update,
        text=_('Здравствуйте! Я бот-психолог. Как можно обращаться к вам?'),
        reply_markup=menu_keyboard()
    )


def ask_focus(update: Update) -> None:
    dialog(
        update,
        text=_('Подведение итогов дня поможет исследовать определенные сложности и паттерны твоего поведения. '
               'Каждую неделю можно выбирать разные фокусы или один и тот же. Выбрать фокус этой недели:'),
        reply_markup=focus_keyboard()
    )


# def button(update: Update, context: CallbackContext) -> int:
def button(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    query.answer()

    user = init_user(update.effective_user)
    set_last_usage(user)
    if query.data.startswith('s_'):
        handle_schedule(update, query)
    elif query.data.startswith('f_'):
        return handle_focus(update, context, query)
    elif query.data.startswith('r_'):
        return handle_ready(update, context, query)

    elif query.data.startswith('m_'):
        handle_mood(update, query)

    elif query.data.startswith('p_'):
        handle_pronoun(update, user, query)
    elif query.data.startswith('c_'):
        handle_conversation_mode(update, context, user, query)
    elif query.data.startswith('q_'):
        handle_questions(update, user, query)
    return ''


def handle_schedule(update, query):
    # User entered schedule
    text = _('Ты выбрал ') + VALUES[query.data] + _(' в качестве времени для рассылки. Спасибо!')

    query.delete_message()
    dialog(update, text=text)
    # query.edit_message_text(text=text)
    ask_focus(update)
    push_user_schedule(update.effective_user, query.data, update.effective_message.date)


def handle_focus(update, context, query):
    # User entered week focus
    set_user_ready_flag(update.effective_user, True)
    push_user_focus(update.effective_user, query.data, update.effective_message.date)
    return engine_callback(update, context)


def handle_ready(update, context, query):
    if query.data == 'r_yes':
        return engine_callback(update, context)
    if query.data == 'r_1h':
        text = _('Понял тебя. Спрошу через час')
        query.edit_message_text(text=text)
        set_user_ready_flag(update.effective_user, True)
    return ''


def handle_pronoun(update, user, query):
    if query.data == 'p_u':
        push_user_pronoun(user, False)
    elif query.data == 'p_you':
        push_user_pronoun(user, True)
    dialog(update, text=_('Спасибо! Ты можешь изменить обращение в любой момент командой /change_pronoun'))


def handle_conversation_mode(update, context, user, query):
    if query.data == 'c_text':
        push_user_mode(user, False)
    elif query.data == 'c_voice':
        push_user_mode(user, True)
    dialog(update, text=_('Спасибо! Ты можешь изменить обращение в любой момент командой /change_mode'))
    ask_start_questions(update, context)


def handle_mood(update, query):
    # User entered mood
    set_user_ready_flag(update.effective_user, True)
    text = _('Ты указал итогом дня ') + VALUES[query.data] + _('. Спасибо!')

    query.delete_message()
    dialog(update, text=text)
    # query.edit_message_text(text=text)

    push_user_feeling(update.effective_user, query.data, update.effective_message.date)

    # debugging zone
    if DEBUG_MODE == DEBUG_ON:
        user = init_user(update.effective_user)
        schedule = get_schedule_by_user(user, is_test=True)
        print(schedule)
        if schedule:
            if len(schedule.sending_list) < DAYS_OFFSET:
                schedule.is_on = True
                schedule.save()


def handle_questions(update, user, query):
    if query.data == 'q_1':
        dialog(update, text=_('Если тебе интересно, то подробнее о методе можно прочитать в книгах Девид Бернса'
                              ' "Терапия Настроения" и Роберта Лихи "Свобода от тревоги".'))
    elif query.data == 'q_2':
        dialog(update, text=_('Методы психотерапии действуют на всех индивидуально и мне сложно прогнозировать '
                              'эффективность, однако, согласно исследованиям эффект может наблюдаются уже через '
                              'месяц регулярных занятий'))
    elif query.data == 'q_3':
        dialog(update, text=_('Для того, чтобы методы'))
    elif query.data == 'q_4':
        dialog(update, text=_('Предлагаемые мной упражнения и практики не являются глубинной работой и играют '
                              'роль как вспомогательное средство. Я не рекомендую данных метод для случаев, когда '
                              'запрос очень тяжелый для тебя'))
    elif query.data == 'q_5':
        dialog(update, text=_('Я передам твой вопрос нашему психологу-консультанту и в ближайшее время пришлю ответ.'))
    elif query.data == 'q_6':
        dialog(update, text=_('Если у тебя нет вопросов, мы можем начать. Расскажи, пожалуйста, максимально подробно,'
                              ' почему ты решил_а обратиться ко мне сегодня, о чем бы тебе хотелось поговорить? '
                              'Наш разговор совершенно конфиденциален'))
        set_user_initial_reason_flag(user, True)


def text_processing(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    if update.message.text == VALUES['menu_share_event']:
        # TODO обработка выбора "поделиться событием"
        pass
    elif update.message.text == VALUES['menu_change_focus']:
        change_focus(update, context)
    elif update.message.text == VALUES['menu_help']:
        help_bot(update, context)
    elif update.message.text == VALUES['change_pronoun']:
        change_pronoun(update, context)
    elif update.message.text == VALUES['change_mode']:
        change_mode(update, context)
    elif get_user_chosen_name(user) == ' ':
        chosen_name = update.message.text
        push_user_chosen_name(user, chosen_name)
        ask_user_pronoun(update, context)
    elif get_user_initial_reason_flag(user):
        reason = update.message.text
        push_user_initial_reason(user, reason)
        set_user_initial_reason_flag(user, False)
        dialog(
            update,
            text=_('В какое время тебе удобно подводить итоги дня?'),
            reply_markup=daily_schedule_keyboard()
        )
    else:
        engine_callback(update, context)


def help_bot(update: Update, context: CallbackContext) -> None:
    user = init_user(update.effective_user)
    set_last_usage(user)
    # TODO сделать справку
    update.message.reply_text('Help!')


def stats(update: Update, context: CallbackContext) -> None:
    user = init_user(update.effective_user)
    set_last_usage(user)
    update.message.reply_text(get_user_feelings(update.effective_user))


def debug_get_users_not_answer_last24hours(update: Update, context: CallbackContext):
    update.message.reply_text('\n'.join(str(item) for item in get_users_not_answer_last24hours()))


def error(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Error!')


def debug_get_users_not_finish_survey(update: Update, context: CallbackContext):
    update.message.reply_text('\n'.join(str(item) for item in get_users_not_finish_survey()))


def ask_ready(updater, schedule):
    # set_schedule_is_on_flag(schedule, False)
    set_schedule_asked_today(schedule)
    updater.bot.send_message(
        schedule.user.id,
        _("Привет! Пришло время подводить итоги. Давай?"),
        reply_markup=ready_keyboard(),
    )


def resume_survey(updater, user) -> None:
    updater.bot.send_message(user, _("Продолжить прохождение опроса?"), reply_markup=ready_keyboard())


def ask_feelings(update: Update, context: CallbackContext) -> None:
    dialog(
        update,
        text=_("Расскажи, как прошел твой день?"),
        reply_markup=mood_keyboard()
    )


# def engine_callback(update, context: CallbackContext) -> int:
def engine_callback(update, context: CallbackContext) -> str:
    engine = Engine(update, context)
    current_step = engine.get_next_step()
    current_step.execute()


def cancel(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    set_last_usage(user)
    dialog(update, text=_('Всего хорошего.'))
    return ConversationHandler.END


def change_focus(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    set_last_usage(user)

    dialog(
        update,
        text=_('Выбери новый фокус:'),
        reply_markup=focus_keyboard()
    )


def send_audio_answer(update: Update, context: CallbackContext):
    update.effective_user.send_message(_("Уже обрабатываю твоё сообщение"))

    text = update.message.text  # 'Спасибо, что поделился своими переживаниями'
    audio = bot_answer_audio(text)

    if audio:
        update.effective_user.send_voice(voice=audio.content)
        # push_bot_answer(update.update_id, answer=audio.content, text=text)
        clear_audio_cache()  # only for testing
    else:
        error(update, context)


def ask_user_pronoun(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    update.message.reply_text(
        f'Приятно познакомиться, {get_user_chosen_name(user)}! Удобно будет на ты или лучше на Вы?',
        reply_markup=pronoun_keyboard()
    )
    ask_user_conversation_mode(update, context)


def ask_user_conversation_mode(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Как бы ты хотел получать мои реплики - в виде текста или голоса?',
        reply_markup=conversation_mode_keyboard()
    )


def change_pronoun(update: Update, context: CallbackContext):
    change_user_pronoun(update.effective_user)
    pronoun = get_user_pronoun(update.effective_user)
    if pronoun:
        update.message.reply_text(
            'Режим общения изменен. Текущий режим: общение на "Вы"'
        )
    else:
        update.message.reply_text(
            'Режим общения изменен. Текущий режим: общение на "Ты"'
        )


def ask_start_questions(update, context):
    dialog(update,
           text=_('Сейчас немного расскажу, как будет устроено наше взаимодействие. Данное приложение построено '
                  'на базе психологической методики под названием "когнитивно-поведенческая терапия" или КПТ. '
                  'Эта методика является одним из современных направлений в психологии и имеет множество клинических '
                  'подтверждений эффективности . Я буду выполнять с тобой несколько упражнений в зависимости от твоего '
                  'запроса, помогу отследить твое состояние, а также мысли и чувства. Есть ли какие-то вопросы?')
           , reply_markup=questions_keyboard())


def change_mode(update: Update, context: CallbackContext):
    change_user_mode(update.effective_user)
    mode = get_user_mode(update.effective_user)
    update.message.reply_text(
        f'Режим общения изменен. Текущий режим: {"текстовые сообщения" if not mode else "голосовые сообщения"}'
    )


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

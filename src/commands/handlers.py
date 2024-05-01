from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)

from databases.db import (
    init_user,
    set_last_usage,
    push_user_schedule,
    set_user_ready_flag,
    push_user_focus,
    push_user_pronoun,
    push_user_mode,
    push_user_feeling,
    get_schedule_by_user,
    set_user_initial_reason_flag,
    get_user_chosen_name,
    push_user_chosen_name,
    get_user_initial_reason_flag,
    push_user_initial_reason,
    set_schedule_asked_today
)

from keyboard import (
    mood_keyboard,
    focus_keyboard,
    ready_keyboard,
    VALUES,
    pronoun_keyboard,
    conversation_mode_keyboard,
    questions_keyboard,
    daily_schedule_keyboard,
)

from modules.tts_module.silero_module import (
    clear_audio_cache,
    bot_answer_audio
)

from utilities import (
    set_translation,
    dialog
)

from env_config import (
    DEBUG_MODE,
    DEBUG_ON
)

from commands.user_commands import (
    change_focus,
    change_mode,
    change_pronoun,
    help_bot
)

from script_engine import Engine

DAYS_OFFSET = 7
PREPARE, TYPING, SELECT_YES_NO, MENU = "PREPARE", "TYPING", "SELECT_YES_NO", "MENU"


def ask_focus(update: Update) -> None:
    user = init_user(update.effective_user)
    translation = set_translation(user)
    dialog(
        update,
        text=translation.gettext(
            'Подведение итогов дня поможет исследовать определенные сложности и паттерны твоего поведения. '
            'Каждую неделю можно выбирать разные фокусы или один и тот же. Выбрать фокус этой недели:'),
        reply_markup=focus_keyboard()
    )


def handle_schedule(update, query):
    user = init_user(update.effective_user)
    translation = set_translation(user)
    # User entered schedule
    text = translation.gettext('Ты выбрал ') + VALUES[query.data] + translation.gettext(
        ' в качестве времени для рассылки. Спасибо!')

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
    user = init_user(update.effective_user)
    translation = set_translation(user)
    if query.data == 'r_yes':
        return engine_callback(update, context)
    if query.data == 'r_1h':
        text = translation.gettext('Понял тебя. Спрошу через час')
        query.edit_message_text(text=text)
        set_user_ready_flag(update.effective_user, True)
    return ''


def handle_pronoun(update, user, query):
    if query.data == 'p_u':
        push_user_pronoun(user, False)
    elif query.data == 'p_you':
        push_user_pronoun(user, True)
    translation = set_translation(user)
    dialog(update,
           text=translation.gettext('Спасибо! Ты можешь изменить обращение в любой момент командой /change_pronoun'))


def handle_conversation_mode(update, context, user, query):
    translation = set_translation(user)
    if query.data == 'c_text':
        push_user_mode(user, False)
    elif query.data == 'c_voice':
        push_user_mode(user, True)
    dialog(update,
           text=translation.gettext('Спасибо! Ты можешь изменить обращение в любой момент командой /change_mode'))
    ask_start_questions(update, context)


def handle_mood(update, query):
    # User entered mood
    user = init_user(update.effective_user)
    translation = set_translation(user)
    set_user_ready_flag(update.effective_user, True)
    text = translation.gettext('Ты указал итогом дня ') + VALUES[query.data] + translation.gettext('. Спасибо!')

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
    translation = set_translation(user)
    if query.data == 'q_1':
        dialog(update, text=translation.gettext(
            'Если тебе интересно, то подробнее о методе можно прочитать в книгах Девид Бернса'
            ' "Терапия Настроения" и Роберта Лихи "Свобода от тревоги".'))
    elif query.data == 'q_2':
        dialog(update, text=translation.gettext(
            'Методы психотерапии действуют на всех индивидуально и мне сложно прогнозировать '
            'эффективность, однако, согласно исследованиям эффект может наблюдаются уже через '
            'месяц регулярных занятий'))
    elif query.data == 'q_3':
        dialog(update, text=translation.gettext('Для того, чтобы методы'))
    elif query.data == 'q_4':
        dialog(update, text=translation.gettext(
            'Предлагаемые мной упражнения и практики не являются глубинной работой и играют '
            'роль как вспомогательное средство. Я не рекомендую данных метод для случаев, когда '
            'запрос очень тяжелый для тебя'))
    elif query.data == 'q_5':
        dialog(update, text=translation.gettext(
            'Я передам твой вопрос нашему психологу-консультанту и в ближайшее время пришлю ответ.'))
    elif query.data == 'q_6':
        dialog(update, text=translation.gettext(
            'Если у тебя нет вопросов, мы можем начать. Расскажи, пожалуйста, максимально подробно,'
            ' почему ты решил_а обратиться ко мне сегодня, о чем бы тебе хотелось поговорить? '
            'Наш разговор совершенно конфиденциален'))
        set_user_initial_reason_flag(user, True)


# def engine_callback(update, context: CallbackContext) -> int:
def engine_callback(update, context: CallbackContext) -> str:
    engine = Engine(update, context)
    current_step = engine.get_next_step()
    current_step.execute()


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


def text_processing(update: Update, context: CallbackContext):
    print(f"Processing {update.message.text}")
    user = init_user(update.effective_user)
    translation = set_translation(user)
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
            text=translation.gettext('В какое время тебе удобно подводить итоги дня?'),
            reply_markup=daily_schedule_keyboard()
        )
    else:
        engine_callback(update, context)


def error(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Error!')


def ask_ready(updater, schedule):
    user = schedule.user
    translation = set_translation(user)
    # set_schedule_is_on_flag(schedule, False)
    set_schedule_asked_today(schedule)
    updater.bot.send_message(
        schedule.user.id,
        translation.gettext("Привет! Пришло время подводить итоги. Давай?"),
        reply_markup=ready_keyboard(),
    )


def resume_survey(updater, user) -> None:
    translation = set_translation(user)
    updater.bot.send_message(user, translation.gettext("Продолжить прохождение опроса?"), reply_markup=ready_keyboard())


def ask_feelings(update: Update, context: CallbackContext) -> None:
    user = init_user(update.effective_user)
    translation = set_translation(user)
    dialog(
        update,
        text=translation.gettext("Расскажи, как прошел твой день?"),
        reply_markup=mood_keyboard()
    )


def cancel(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    set_last_usage(user)
    translation = set_translation(user)
    dialog(update, text=translation.gettext('Всего хорошего.'))
    return ConversationHandler.END


def send_audio_answer(update: Update, context: CallbackContext):
    user = init_user(update.effective_user)
    translation = set_translation(user)
    update.effective_user.send_message(translation.gettext("Уже обрабатываю твоё сообщение"))

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
        'Как бы Вы хотели получать мои реплики - в виде текста или голоса?',
        reply_markup=conversation_mode_keyboard()
    )


def ask_start_questions(update, context):
    user = init_user(update.effective_user)
    translation = set_translation(user)
    dialog(update,
           text=translation.gettext(
               'Сейчас немного расскажу, как будет устроено наше взаимодействие. Данное приложение построено '
               'на базе психологической методики под названием "когнитивно-поведенческая терапия" или КПТ. '
               'Эта методика является одним из современных направлений в психологии и имеет множество клинических '
               'подтверждений эффективности . Я буду выполнять с тобой несколько упражнений в зависимости от твоего '
               'запроса, помогу отследить твое состояние, а также мысли и чувства. Есть ли какие-то вопросы?')
           , reply_markup=questions_keyboard())
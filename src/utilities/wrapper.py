from telegram import Update

from modules.tts_module.silero_module import (
    bot_answer_audio,
)

from env_config import (
    DEBUG_MODE,
    DEBUG_ON,
    DEBUG_OFF
)

from databases.db import get_user_mode


def dialog(update: Update, text: str, reply_markup=None) -> None:

    mode = get_user_mode(update.effective_user)
    if mode:
        try:
            audio = bot_answer_audio(text)

        except ConnectionError as synthesis_error:
            if DEBUG_MODE == DEBUG_ON:
                raise synthesis_error
            if DEBUG_MODE == DEBUG_OFF:
                update.message.reply_text('Ошибка в синтезе речи, попробуйте позже.')

        else:
            update.effective_user.send_voice(voice=audio.content, reply_markup=reply_markup)

    else:
        update.effective_user.send_message(text=text, reply_markup=reply_markup)

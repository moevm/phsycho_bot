from telegram import Update
from silero_module import bot_answer_audio, clear_audio_cache

from env_config import (DEBUG_MODE, DIALOG_MODE,
                        TEXT_MODE, VOICE_MODE, DEBUG_ON, DEBUG_OFF)


def dialog(update: Update, text: str, reply_markup=None) -> None:
    mode = get_user_mode(update.effective_user)
    if mode:
        audio = bot_answer_audio(text)

        if audio:
            update.effective_user.send_voice(voice=audio.content, reply_markup=reply_markup)
            clear_audio_cache()
        else:
            update.message.reply_text('Error!')

    else:
        update.effective_user.send_message(text=text, reply_markup=reply_markup)

def dialog_wrapper(update: Update, text: str, reply_markup=None) -> None:

    if DIALOG_MODE == VOICE_MODE:

        try:
            audio = bot_answer_audio(text)

        except ConnectionError as synthesis_error:
            if DEBUG_MODE == DEBUG_ON:
                raise synthesis_error
            if DEBUG_MODE == DEBUG_OFF:
                update.message.reply_text('Ошибка в синтезе речи, попробуйте позже.')

        else:
            update.effective_user.send_voice(voice=audio.content, reply_markup=reply_markup)
            clear_audio_cache()

    elif DIALOG_MODE == TEXT_MODE:
        update.effective_user.send_message(text=text, reply_markup=reply_markup)

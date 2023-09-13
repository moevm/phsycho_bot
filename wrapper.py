from telegram import Update
from silero_module import bot_answer_audio, clear_audio_cache

from config import (DEBUG_MODE, DIALOG_MODE,
                    TEXT_MODE, VOICE_MODE, DEBUG_ON, DEBUG_OFF)


def dialog_wrapper(update: Update, text: str, reply_markup=None) -> None:

    if DIALOG_MODE == VOICE_MODE:

        try:
            audio = bot_answer_audio(text)

        except Exception as er:
            if DEBUG_MODE == DEBUG_ON:
                raise er
            elif DEBUG_MODE == DEBUG_OFF:
                update.message.reply_text('Ошибка в синтезе речи, попробуйте позже.')

        else:
            update.effective_user.send_voice(voice=audio.content, reply_markup=reply_markup)
            clear_audio_cache()

    elif DIALOG_MODE == TEXT_MODE:
        update.effective_user.send_message(text=text, reply_markup=reply_markup)

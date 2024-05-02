import json
import ast

from telegram import Update
import requests


from kafka.kafka_producer import produce_message
from modules.tts_module.silero_module import (
    bot_answer_audio
)

from env_config import (
    DEBUG_MODE,
    DEBUG_ON,
    DEBUG_OFF,
    TOKEN
)

from databases.db import get_user_mode


def dialog(update: Update, text: str, reply_markup=None) -> None:
    mode = get_user_mode(update.effective_user)
    if mode:
        message = {
            'user': update.effective_user.to_dict(),
            'text': text,
            'reply_markup': json.dumps(ast.literal_eval(str(reply_markup)))
        }
        produce_message('tts', json.dumps(message))

    else:
        update.effective_user.send_message(text=text, reply_markup=reply_markup)


def send_voice(text, user, reply_markup):
    try:
        audio = bot_answer_audio(text)
    except ConnectionError as synthesis_error:
        if DEBUG_MODE == DEBUG_ON:
            raise synthesis_error
        if DEBUG_MODE == DEBUG_OFF:
            url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
            data = {
                'chat_id': user.id,
                'text': 'Ошибка в синтезе речи, попробуйте позже.'
            }

            response = requests.post(url, json=data, timeout=3)

    else:

        data = {
            'reply_markup': reply_markup,
        } if json.loads(reply_markup) is not None else {}

        files = {
            'voice': audio.content
        }

        url = f"https://api.telegram.org/bot{TOKEN}/sendVoice?chat_id={str(user.id)}&voice="

        response = requests.post(url, data=data, files=files)

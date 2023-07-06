import os
import requests
import time


class VoiceSettings:
    link = 'http://silero-tts-service'
    speaker = os.environ.get('SPEAKER')

    language = os.environ.get('LANGUAGE')
    sample_rate = os.environ.get('SAMPLE_RATE')


def bot_answer_audio(bot_text):

    request_params = {'VOICE': VoiceSettings.speaker, 'INPUT_TEXT': bot_text}
    try:
        answer = requests.get(VoiceSettings.link + '/process', params=request_params)
    except ConnectionError:
        return None

    return answer


def clear_audio_cache():
    try:
        return requests.get(VoiceSettings.link + '/clear_cache')
    except ConnectionError:
        return None

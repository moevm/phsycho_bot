import os
import requests
import time


class SpeakerSettings:
    language = os.environ.get('LANGUAGE')
    model_id = os.environ.get('MODEL_ID')
    sample_rate = int(os.environ.get('SAMPLE_RATE'))
    speaker = os.environ.get('SPEAKER')


def bot_answer_audio(bot_text):

    request_params = {'voice': SpeakerSettings.speaker, 'text': bot_text}
    answer = requests.get('https://silero-tts-service/process', params=request_params)

    return answer


def clear_audio_cache():
    return requests.get('https://silero-tts-service/clear_cache')


def get_bot_voices():
    return requests.get('https://silero-tts-service/voices')


def get_bot_settings():
    return requests.get('https://silero-tts-service/settings')

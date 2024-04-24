import requests

from env_config import (
    SPEAKER,
    LANGUAGE,
    SAMPLE_RATE
)


class VoiceSettings:
    link = 'http://silero-tts-service:9898'
    speaker = SPEAKER
    language = LANGUAGE
    sample_rate = SAMPLE_RATE


def bot_answer_audio(bot_text):
    request_params = {'VOICE': VoiceSettings.speaker, 'INPUT_TEXT': bot_text}
    return requests.get(VoiceSettings.link + '/process', params=request_params)


def clear_audio_cache():
    try:
        return requests.get(VoiceSettings.link + '/clear_cache')
    except requests.exceptions.RequestException:
        return None

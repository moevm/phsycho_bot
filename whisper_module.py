import requests

from env_config import ASR_ENGINE, ASR_MODEL


class WhisperSettings:
    link = 'http://whisper-asr-webservice:9000'
    asr_engine = ASR_ENGINE
    asr_model = ASR_MODEL


def get_att_whisper(filename, output: str = 'json'):
    """
     filename: str
        audio file name

    output characteristics
        possible return object types:
            "txt", "vtt", "srt", "tsv", "json"
    """

    file = {'audio_file': (filename, open(filename, 'rb'))}
    data = {'task': 'transcribe', 'output': output, 'word_timestamps': 'true'}
    response = requests.post(WhisperSettings.link + '/asr', data=data, files=file)

    return response

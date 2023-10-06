import requests

from env_config import ASR_ENGINE, ASR_MODEL


class WhisperSettings:
    link = 'http://whisper-asr-webservice:9000'
    asr_engine = ASR_ENGINE
    asr_model = ASR_MODEL


def get_att_whisper(filename):
    """
     filename: str
        audio file name

    output characteristics
        possible return object types:
            "txt", "vtt", "srt", "tsv", "json"
    """

    with open(filename, 'rb') as f_byte:
        file = {'audio_file': (filename, f_byte)}

        response = requests.post(WhisperSettings.link +
                                 '/asr?task=transcribe&encode=false&output=json&word_timestamps=true',
                                 files=file)

    return response

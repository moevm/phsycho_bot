import requests

from env_config import ASR_ENGINE, ASR_MODEL


class WhisperSettings:
    link = 'http://whisper-asr-webservice:9000'
    asr_engine = ASR_ENGINE
    asr_model = ASR_MODEL


def audio_to_text(file, output: str = 'txt'):
    """
     file: BinaryIO
        The audio file like object

    output characteristics
        possible return object types:
            "txt", "vtt", "srt", "tsv", "json"
    """
    request_params = {'audio_file': file, 'output': output, 'word_timestamps': True}
    result = requests.get(WhisperSettings.link + '/asr', params=request_params)
    return result


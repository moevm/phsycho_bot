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

    file = {'file': open(filename, 'rb')}

    request_params = {'task': 'transcribe', 'audio_file': file, 'output': output}
    return requests.get(WhisperSettings.link + '/asr', params=request_params)


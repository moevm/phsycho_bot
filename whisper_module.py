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

    with open(filename, "rb") as file:
        file_dict = {filename: file}

    request_params = {'audio_file': file_dict, 'output': output}
    response = requests.post(WhisperSettings.link + '/asr', data=request_params)

    return response

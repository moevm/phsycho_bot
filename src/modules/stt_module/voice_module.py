import json
import os
import subprocess

from noisereduce import reduce_noise
from scipy.io import wavfile
from telegram import Update
from telegram.ext import CallbackContext
from bson import json_util

from src.modules.stt_module.whisper_module import get_att_whisper
from src.modules.stt_module.audio_classes import RecognizedSentence
from src.databases.db import push_user_survey_progress, init_user, get_user_audio

from src.env_config import (DEBUG_MODE,
                            DEBUG_ON, DEBUG_OFF)


def audio_to_text(filename):
    response = get_att_whisper(filename)

    if response.status_code == 200:

        input_sentence = RecognizedSentence(response.json())
        return input_sentence

    return None


def download_voice(update: Update):
    downloaded_file = update.message.voice.get_file()
    voice_bytearray = downloaded_file.download_as_bytearray()

    ogg_filename = os.path.join('user_voices', f'user_{update.message.chat.id}')
    if not os.path.exists(ogg_filename):
        os.makedirs(ogg_filename)
    ogg_filename += f"/{downloaded_file.file_unique_id}.ogg"

    with open(ogg_filename, "wb") as voice_file:
        voice_file.write(voice_bytearray)
    wav_filename = ogg_filename.split(".")[0] + ".wav"

    # 16000 - частота дискретизации, 1 - кол-во аудиоканалов, 256К - битрейт
    command = f"ffmpeg -i {ogg_filename} -ar 16000 -ac 1 -ab 256K -f wav {wav_filename}"
    subprocess.run(command.split())
    return (wav_filename, ogg_filename)


def noise_reduce(input_audio):
    """
         input_audio: str
            audio file name (*.wav)

        output: str
            audio without noise file name (*_nonoise.wav)
    """
    rate, data = wavfile.read(input_audio)
    date_noise_reduce = reduce_noise(y=data, sr=rate)
    output_audio_without_noise = input_audio.split('.')[0] + "_nonoise.wav"
    wavfile.write(output_audio_without_noise, rate, date_noise_reduce)
    return output_audio_without_noise


def work_with_audio(update: Update, context: CallbackContext):
    wav_filename, ogg_filename = download_voice(update)
    no_noise_audio = noise_reduce(wav_filename)

    try:
        input_sentence = audio_to_text(no_noise_audio)
    except IOError as e:
        raise e

    stats_sentence = input_sentence.generate_stats()

    if DEBUG_MODE == DEBUG_ON:
        update.effective_user.send_message(input_sentence.generate_output_info())

    elif DEBUG_MODE == DEBUG_OFF:
        pass

    push_user_survey_progress(
        update.effective_user,
        init_user(update.effective_user).get_last_focus(),
        update.update_id,
        user_answer=input_sentence.get_text(),
        stats=stats_sentence,
        audio_file=open(ogg_filename, 'rb'),  # pylint: disable=consider-using-with
    )
    os.remove(ogg_filename)

    if DEBUG_MODE == DEBUG_ON:
        print(get_user_audio(update.effective_user))
        update.effective_user.send_message(
            "ID записи с твоим аудиосообщением в базе данных: "
            + str(json.loads(json_util.dumps(get_user_audio(update.effective_user))))
        )

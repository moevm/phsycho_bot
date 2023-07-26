import json
import os
import subprocess

from noisereduce import reduce_noise
from scipy.io import wavfile
from telegram import Update
from telegram.ext import CallbackContext
import whisper
from bson import json_util

from audio_classes import RecognizedSentence
from db import push_user_survey_progress, init_user, get_user_audio

model = whisper.load_model("base")


def audio_to_text(filename):
    transcription = model.transcribe(filename, word_timestamps=True)
    result_json = json.dumps(transcription)

    recognized_data = json.loads(result_json)
    input_sentence = RecognizedSentence(recognized_data)
    return input_sentence


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
    rate, data = wavfile.read(input_audio)
    date_noise_reduce = reduce_noise(y=data, sr=rate)
    output_audio_without_noise = input_audio.split('.')[0] + "_nonoise.wav"
    wavfile.write(output_audio_without_noise, rate, date_noise_reduce)
    return output_audio_without_noise


def work_with_audio(update: Update, context: CallbackContext):
    wav_filename, ogg_filename = download_voice(update)
    no_noise_audio = noise_reduce(wav_filename)
    input_sentence = audio_to_text(no_noise_audio)
    stats_sentence = input_sentence.generate_stats()
    debug = os.environ.get("DEBUG_MODE")
    if debug == "true":
        update.effective_user.send_message(input_sentence.generate_output_info())
    elif debug == "false":
        pass
    push_user_survey_progress(
        update.effective_user,
        init_user(update.effective_user).focuses[-1]['focus'],
        update.update_id,
        user_answer=input_sentence._text,
        stats=stats_sentence,
        audio_file=open(ogg_filename, 'rb'),  # pylint: disable=consider-using-with
    )
    os.remove(ogg_filename)
    if debug == "true":
        print(get_user_audio(update.effective_user))
        update.effective_user.send_message(
            "ID записи с твоим аудиосообщением в базе данных: "
            + str(json.loads(json_util.dumps(get_user_audio(update.effective_user))))
        )

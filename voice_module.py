import os
import subprocess

from telegram import Update
from telegram.ext import CallbackContext
from db import init_survey_progress, init_user


def download_voice(update: Update):
    downloaded_file = update.message.voice.get_file()
    voice_bytearray = downloaded_file.download_as_bytearray()
    ogg_filename = os.path.join('user_voices', f'user_{update.message.chat.id}')
    if not os.path.exists(ogg_filename):
        os.makedirs(ogg_filename)
    ogg_filename += f"/{downloaded_file.file_unique_id}.ogg"
    with open(ogg_filename, "wb") as voice_file:
        voice_file.write(voice_bytearray)
    wav_filename = ogg_filename.split(".")[0]+".wav"
    command = f"ffmpeg -i {ogg_filename} -ar 16000 -ac 1 -ab 256K -f wav {wav_filename}" #16000 - частота дискретизации, 1 - кол-во аудиоканалов, 256К - битрейт
    subprocess.run(command.split())
    os.remove(ogg_filename)
    return wav_filename


def work_with_audio(update: Update, context: CallbackContext):
    wav_filename = download_voice(update)
    init_survey_progress(update.effective_user, init_user(update.effective_user).focuses[-1]['focus'], update.update_id, user_answer=wav_filename)



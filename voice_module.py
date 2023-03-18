import json
import os, sys
import subprocess
import wave
# import soundfile

import pyttsx3
from telegram import Update
from telegram.ext import CallbackContext
from vosk import KaldiRecognizer, Model
from pydub import AudioSegment

model = Model(os.path.join("model", "vosk-model-small-ru-0.22"))
engine = pyttsx3.init()


def audio_to_text(filename):
    wf = wave.open(filename, "rb")
    rec = KaldiRecognizer(model, 24000)
    data = wf.readframes(wf.getnframes())
    rec.AcceptWaveform(data)
    recognized_data = json.loads(rec.Result())["text"]
    return recognized_data


def text_to_audio(text_to_convert, wav_filename):
    output_filename_mp3 = wav_filename.split(".")[0]+"_answer.mp3"
    print(text_to_convert)
    engine.save_to_file(text_to_convert, output_filename_mp3)
    engine.runAndWait()
    return output_filename_mp3


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
    input_text = audio_to_text(wav_filename)
    output_file = text_to_audio(input_text, wav_filename)
    update.effective_user.send_message(input_text)

# def convert_wav_to_ogg(wav_filename):
#     data, samplerate = soundfile.read(wav_filename)
#     ogg_file = soundfile.write('newfile.ogg', data, samplerate)
#     return ogg_file

def convert_wav_to_ogg(wav_filename):
    wav_file = "wav_filename.wav"
    ogg_file = os.path.splitext("wav_filename.wav")[0]+".ogg"
    voice = AudioSegment.from_wav(wav_file)
    voice.export(ogg_file, format="ogg")
    return voice

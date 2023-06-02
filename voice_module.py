import json
import os
import subprocess
import wave

from noisereduce import reduce_noise
from scipy.io import wavfile
from telegram import Update
from telegram.ext import CallbackContext
from vosk import KaldiRecognizer, Model

from audio_classes import RecognizedSentence
from db import push_user_survey_progress, init_user, get_user_audio

model = Model(os.path.join("model", "vosk-model-small-ru-0.22"))

def audio_to_text(filename):
    wf = wave.open(filename, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    while True:
        data = wf.readframes(1000)
        if len(data) == 0:
            break
        rec.AcceptWaveform(data)
    wf.close()
    recognized_data = json.loads(rec.FinalResult())
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
    wav_filename = ogg_filename.split(".")[0]+".wav"
    command = f"ffmpeg -i {ogg_filename} -ar 16000 -ac 1 -ab 256K -f wav {wav_filename}" #16000 - частота дискретизации, 1 - кол-во аудиоканалов, 256К - битрейт
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
    #output_file = text_to_audio(input_text, wav_filename)
    update.effective_user.send_message(input_sentence.generate_output_info())
    push_user_survey_progress(update.effective_user, init_user(update.effective_user).focuses[-1]['focus'], update.update_id, user_answer=input_sentence._text, stats=stats_sentence, audio_file=open(ogg_filename, 'rb'))
    os.remove(ogg_filename)
    with open('text.ogg', 'wb') as f:
        f.write(get_user_audio(update.effective_user))
    with open('text.ogg', 'rb') as f:
        update.effective_user.send_audio(f)
    #update.effective_user.send_message(get_user_audio(update.effective_user))
    #возвращение пользователю голосового из бд для проверки корректности сохранения

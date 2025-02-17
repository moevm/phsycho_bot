import json
import os
import subprocess
import requests

from noisereduce import reduce_noise
from scipy.io import wavfile
from telegram import Update
from telegram.ext import CallbackContext
from bson import json_util
from pydub import AudioSegment
from pydub.silence import detect_silence

from modules.stt_module.whisper_module import get_att_whisper
from modules.stt_module.audio_classes import RecognizedSentence
from databases.db import push_user_survey_progress, init_user, get_user_audio

from env_config import (DEBUG_MODE,
                        DEBUG_ON, DEBUG_OFF, TOKEN)
from kafka.kafka_producer import produce_message


def split_audio(wav_filename, min_chunk_length=30000, max_chunk_length=40000, silence_thresh=-40, min_silence_len=500):
    audio = AudioSegment.from_wav(wav_filename)
    chunk_filenames = []

    if len(audio) <= min_chunk_length:
        chunk_filename = wav_filename.replace(".wav", "_chunk_0.wav")
        audio.export(chunk_filename, format="wav")
        return [chunk_filename]

    silence_ranges = detect_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    silence_points = [(start + end) / 2 for start, end in silence_ranges]

    chunks = []
    start = 0

    for silence in silence_points:
        chunk_length = silence - start
        if min_chunk_length <= chunk_length <= max_chunk_length:
            chunks.append(audio[start:silence])
            start = silence
        elif chunk_length > max_chunk_length:
            split_point = start + max_chunk_length
            chunks.append(audio[start:split_point])
            start = split_point

    if start < len(audio):
        chunks.append(audio[start:])

    for i, chunk in enumerate(chunks):
        chunk_filename = wav_filename.replace(".wav", f"_chunk_{i}.wav")
        chunk.export(chunk_filename, format="wav")
        chunk_filenames.append(chunk_filename)

    return chunk_filenames


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

    chunk_filenames = split_audio(wav_filename)

    return (wav_filename, ogg_filename, chunk_filenames)


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
    wav_filename, ogg_filename, chunk_filenames = download_voice(update)
    no_noise_audio = noise_reduce(wav_filename)
    message = {
        'user': update.effective_user.to_dict(),
        'update_id': update.update_id,
        'filename': no_noise_audio,
        'ogg_filename': ogg_filename,
        'chunk_filenames': chunk_filenames
    }
    produce_message('stt', json.dumps(message))


def audio_to_text(filename, ogg_filename, chunk_filenames, update_id, user):
    input_sentence, stats_sentence = "", ""
    for chunk_filename in chunk_filenames:
        response = get_att_whisper(chunk_filename)

        if response.status_code == 200:
            chunk_input_sentence = RecognizedSentence(response.json())
        else:
            return

        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
        data = {
            'chat_id': user.id,
            'text': chunk_input_sentence.generate_output_info()
        }

        chunk_stats_sentence = chunk_input_sentence.generate_stats()

        if DEBUG_MODE == DEBUG_ON:
            response = requests.post(url, json=data)

            if response.status_code == 200:
                print('Request send successfully')
            else:
                print(f'Error sending request: {response.json()["description"]}')

        elif DEBUG_MODE == DEBUG_OFF:
            pass

        input_sentence += chunk_input_sentence.get_text()
        stats_sentence += chunk_stats_sentence + "\n"

    push_user_survey_progress(
        user,
        init_user(user).get_last_focus(),
        update_id,
        user_answer=input_sentence,
        stats=stats_sentence,
        audio_file=open(ogg_filename, 'rb'),  # pylint: disable=consider-using-with
    )
    os.remove(ogg_filename)

    if DEBUG_MODE == DEBUG_ON:
        print(get_user_audio(user))
        user.effective_user.send_message(
            "ID записи с твоим аудиосообщением в базе данных: "
            + str(json.loads(json_util.dumps(get_user_audio(user))))
        )

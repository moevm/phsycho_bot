import json
import os
import time
import subprocess
from noisereduce import reduce_noise
from scipy.io import wavfile
from telegram import Update
from telegram.ext import CallbackContext
from bson import json_util
from pydub import AudioSegment
from pydub.silence import detect_silence

from modules.stt_module.whisper_module import get_att_whisper
from modules.stt_module.audio_classes import RecognizedSentence
from emotion_analysis import associate_words_with_emotions
from utilities.wrapper import send_text
from databases.db import push_user_survey_progress, init_user, get_user_audio

from env_config import (DEBUG_MODE, DEBUG_ON)
from kafka.kafka_producer import produce_message


def get_silence_points(audio, min_silence_len, silence_thresh):
    silence_ranges = detect_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    return [(start + end) / 2 for start, end in silence_ranges]


def generate_chunks(audio, silence_points, min_len, max_len):
    chunks = []
    starts = []
    start = 0

    for silence in silence_points:
        chunk_length = silence - start
        if min_len <= chunk_length <= max_len:
            chunks.append(audio[start:int(silence)])
            starts.append(start)
            start = int(silence)
        elif chunk_length > max_len:
            split_point = start + max_len
            chunks.append(audio[start:split_point])
            starts.append(start)
            start = split_point

    if start < len(audio):
        chunks.append(audio[start:])
        starts.append(start)

    return chunks, starts


def export_chunks(chunks, base_dir, file_id):
    filenames = []
    for i, chunk in enumerate(chunks):
        filename = os.path.join(base_dir, f"{file_id}_chunk_{i}.wav")
        chunk.export(filename, format="wav")
        filenames.append(filename)
    return filenames


def split_audio(wav_filename, unique_file_id, min_chunk_length=30000, max_chunk_length=40000, silence_thresh=-40,
                min_silence_len=500):
    audio = AudioSegment.from_wav(wav_filename)
    chunk_dir = os.path.join('emotion_recognition', 'input_files')
    if not os.path.exists(chunk_dir):
        os.makedirs(chunk_dir)

    if len(audio) <= min_chunk_length:
        filename = os.path.join(chunk_dir, f"{unique_file_id}_chunk_0.wav")
        audio.export(filename, format="wav")
        return [filename], [0]

    silence_points = get_silence_points(audio, min_silence_len, silence_thresh)
    chunks, start_times = generate_chunks(audio, silence_points, min_chunk_length, max_chunk_length)
    filenames = export_chunks(chunks, chunk_dir, unique_file_id)

    return filenames, start_times


def download_voice(update: Update):
    downloaded_file = update.message.voice.get_file()
    voice_bytearray = downloaded_file.download_as_bytearray()

    unique_file_id = downloaded_file.file_unique_id

    ogg_filename = os.path.join('user_voices', f'user_{update.message.chat.id}')
    if not os.path.exists(ogg_filename):
        os.makedirs(ogg_filename)
    ogg_filename += f"/{unique_file_id}.ogg"

    with open(ogg_filename, "wb") as voice_file:
        voice_file.write(voice_bytearray)
    wav_filename = ogg_filename.split(".")[0] + ".wav"

    # 16000 - частота дискретизации, 1 - кол-во аудиоканалов, 256К - битрейт
    command = f"ffmpeg -i {ogg_filename} -ar 16000 -ac 1 -ab 256K -f wav {wav_filename}"
    subprocess.run(command.split())

    no_noise_audio = noise_reduce(wav_filename)
    chunk_filenames, chunk_start_times = split_audio(no_noise_audio, unique_file_id)

    return (wav_filename, ogg_filename, chunk_filenames, chunk_start_times)


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
    wav_filename, ogg_filename, chunk_filenames, chunk_start_times = download_voice(update)
    message = {
        'user': update.effective_user.to_dict(),
        'update_id': update.update_id,
        'filename': wav_filename,
        'ogg_filename': ogg_filename,
        'chunk_filenames': chunk_filenames,
        'chunk_start_times': chunk_start_times
    }
    produce_message('stt', json.dumps(message))


def process_chunk(chunk_filename, start_time):
    response = get_att_whisper(chunk_filename)

    if response.status_code != 200:
        return None

    sentence = RecognizedSentence(response.json())
    word, emotion = associate_words_with_emotions(os.path.basename(chunk_filename), sentence.get_text())

    return {
        "text": sentence.get_text(),
        "stats": sentence.generate_stats(),
        "emotion": emotion,
        "word": word,
        "start_time": start_time,
        "filename": chunk_filename,
    }


def audio_to_text(filename, ogg_filename, chunk_filenames, chunk_start_times, update_id, user):
    start_time = time.time()
    full_text = []
    stats_blocks = []
    emotion_stats = []

    for chunk_filename, start_time_chunk in zip(chunk_filenames, chunk_start_times):
        result = process_chunk(chunk_filename, start_time_chunk)
        if not result:
            return

        full_text.append(result["text"])
        stats_blocks.append(result["stats"])
        emotion_stats.append({
            "filename": result["filename"],
            "emotion": result["emotion"],
            "word": result["word"],
            "text": result["text"],
            "start_time": result["start_time"]
        })

    if DEBUG_MODE == DEBUG_ON:
        elapsed = time.time() - start_time
        send_text(user.id, f"Время обработки: {elapsed:.2f} секунд")
        formatted_stats = "\n\n".join([
            f"Файл: {stat['filename']}\n"
            f"Эмоция: {stat['emotion']}\n"
            f"Слово: \"{stat['word']}\"\n"
            f"Фраза: \"{stat['text']}\"\n"
            f"Начало: {stat['start_time']:.2f} сек"
            for stat in emotion_stats
        ])
        send_text(user.id, f"Статистика эмоций:\n{formatted_stats}")

    push_user_survey_progress(
        user=user,
        focus=init_user(user).get_last_focus(),
        id_=update_id,
        user_answer="".join(full_text),
        stats="\n".join(stats_blocks),
        audio_file=open(ogg_filename, 'rb'),  # pylint: disable=consider-using-with
        audio_emotions_statistics=emotion_stats
    )

    os.remove(ogg_filename)

    if DEBUG_MODE == DEBUG_ON:
        print(get_user_audio(user))
        send_text(user.id, "ID записи с твоим аудиосообщением в базе данных: " +
                  str(json.loads(json_util.dumps(get_user_audio(user)))))

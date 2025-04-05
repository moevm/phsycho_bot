import json
import os
import subprocess
import time

from telegram import Update
from telegram.ext import CallbackContext
from bson import json_util

from emotion_analysis import predict_emotion
from modules.stt_module.whisper_module import get_att_whisper
from modules.stt_module.audio_classes import RecognizedSentence
from modules.stt_module.voice_module import noise_reduce
from databases.db import push_user_survey_progress, init_user, get_user_video
from env_config import (DEBUG_MODE, DEBUG_ON, DEBUG_OFF, TOKEN)
from kafka.kafka_producer import produce_message
from utilities.wrapper import send_text


def extract_audio_pydub(video_path):
    output_audio_path = video_path.replace(".mp4", ".wav")
    ogg_audio_path = video_path.replace(".mp4", ".ogg")

    command = f"ffmpeg -i {video_path} -vn -acodec pcm_s16le -ar 16000 -ac 1 {output_audio_path}"
    subprocess.run(command.split(), check=True)

    command = f"ffmpeg -i {video_path} -vn -acodec libvorbis {ogg_audio_path}"
    subprocess.run(command.split(), check=True)

    print(f"Audio saved: {output_audio_path}")
    return output_audio_path, ogg_audio_path


def download_video(update: Update):
    if update.message.video_note:
        video_file = update.message.video_note
    else:
        video_file = update.message.video
    downloaded_file = video_file.get_file()
    video_bytearray = downloaded_file.download_as_bytearray()

    video_dir = os.path.join('user_videos', f'user_{update.message.chat.id}')
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)

    emotion_files_dir_name = os.path.join('emotion_recognition', 'input_files')
    if not os.path.exists(emotion_files_dir_name):
        os.makedirs(emotion_files_dir_name)

    mp4_filename = os.path.join(video_dir, f"{downloaded_file.file_unique_id}.mp4")
    mp4_filename_emotion_dir = os.path.join(emotion_files_dir_name, f"{downloaded_file.file_unique_id}.mp4")

    with open(mp4_filename, "wb") as video_file:
        video_file.write(video_bytearray)

    with open(mp4_filename_emotion_dir, "wb") as video_file:
        video_file.write(video_bytearray)

    return mp4_filename, mp4_filename_emotion_dir


def work_with_video(update: Update, context: CallbackContext):
    video_path, emotion_dir_video_path = download_video(update)

    message = {
        'user': update.effective_user.to_dict(),
        'update_id': update.update_id,
        'video_path': video_path,
        'emotion_dir_video_path': emotion_dir_video_path
    }
    produce_message('video', json.dumps(message))


def process_video(video_path, emotion_dir_video_path, update_id, user):
    start_time = time.time()

    emotion = predict_emotion(emotion_dir_video_path)

    if DEBUG_MODE == DEBUG_ON:
        end_time = time.time()
        processing_time = end_time - start_time
        send_text(user.id, f"Processing time: {processing_time:.2f} seconds")

    send_text(user.id, f"Result emotion: {emotion}")

    audio_path, ogg_filename = extract_audio_pydub(video_path)
    no_noise_audio = noise_reduce(audio_path)
    response = get_att_whisper(no_noise_audio)
    input_sentence = RecognizedSentence(response.json())

    if DEBUG_MODE == DEBUG_ON:
        send_text(user.id, input_sentence.generate_output_info())

    push_user_survey_progress(
        init_user(user),
        init_user(user).get_last_focus(),
        update_id,
        user_answer=input_sentence.get_text(),
        stats=input_sentence.generate_stats(),
        audio_file=open(ogg_filename, 'rb'),
        video_file=open(video_path, 'rb'),
        emotion=emotion
    )
    os.remove(ogg_filename)

    if DEBUG_MODE == DEBUG_ON:
        print(get_user_video(user))
        send_text(user.id, "ID записи с твоим видеосообщением в базе данных: "
                  + str(json.loads(json_util.dumps(get_user_video(user)))))

import os
from telegram import Update
from telegram.ext import CallbackContext

from emotion_analysis import predict_emotion


def download_video(update: Update):
    video_file = update.message.video_note
    downloaded_file = video_file.get_file()
    video_bytearray = downloaded_file.download_as_bytearray()

    video_dir = os.path.join('user_videos', f'user_{update.message.chat.id}')
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)

    emotion_files_dir_name = os.path.join('emotion_recognition', 'input_files')
    if not os.path.exists(emotion_files_dir_name):
        os.makedirs(emotion_files_dir_name)


    mp4_filename = os.path.join(video_dir, f"{downloaded_file.file_unique_id}.mp4")
    mp4_filename_emotion = os.path.join(emotion_files_dir_name, f"{downloaded_file.file_unique_id}.mp4")

    with open(mp4_filename, "wb") as video_file:
        video_file.write(video_bytearray)

    with open(mp4_filename_emotion, "wb") as video_file:
        video_file.write(video_bytearray)

    return mp4_filename, mp4_filename_emotion

def work_with_video(update: Update, context: CallbackContext):
    video_path, emotion_video_path = download_video(update)

    print(f"VIDEO SAVED: {video_path}")
    emotion = predict_emotion(emotion_video_path)
    update.effective_user.send_message(f"Result emotion: {emotion}")
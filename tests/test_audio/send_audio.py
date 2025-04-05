import os, sys
import asyncio
import librosa
from pyrogram import Client, filters
from pyrogram.types import Message

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from create_app import create_app

AUDIO_FOLDER = 'audio_messages'

user_response = None
response_event = asyncio.Event()

def get_audio_duration(file_path):
    audio_data, sample_rate = librosa.load(file_path)
    duration = librosa.get_duration(y=audio_data, sr=sample_rate)
    return duration


async def handle_message(client: Client, message: Message):
    global user_response
    user_response = message.text
    response_event.set()


async def send_audio_and_wait(app: Client, username: str, filename: str):
    print(f"Sending video: {filename}")

    await app.send_audio(username, filename)

    await response_event.wait()
    response_event.clear()

    return user_response


async def main():
    app, username = create_app()

    @app.on_message(filters.text & filters.private)
    async def message_handler(client: Client, message: Message):
        await handle_message(client, message)

    await app.start()

    for root, _, files in os.walk(AUDIO_FOLDER):
        for file in files:
            if file.lower().endswith('.mp4'):
                filename = os.path.join(root, file)

                response = await send_audio_and_wait(app, username, filename)
                if response:
                    processing_time = float(str(response).split(": ")[1].split(" ")[0])
                    audio_duration = get_audio_duration(filename)
                    print(f"Filename: {filename}, Processing time: {processing_time:.2f} seconds, "
                          f"Audio duration: {audio_duration:.2f} seconds")

    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())

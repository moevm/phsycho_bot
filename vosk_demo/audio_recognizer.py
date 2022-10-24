import json
import wave
import subprocess
import os

from vosk import KaldiRecognizer, Model  # оффлайн-распознавание от Vosk


def recognizer(file_path):
    wav_path = "." + file_path.split('.')[1] + ".wav"

    # convert oog to wav
    command = f"ffmpeg -i {file_path} -ar 16000 -ac 2 -ab 192K -f wav {wav_path}"
    _ = subprocess.check_call(command.split())

    model = Model("./model/")

    wave_audio_file = wave.open(wav_path, "rb")
    offline_recognizer = KaldiRecognizer(model, 24000)
    data = wave_audio_file.readframes(wave_audio_file.getnframes())

    offline_recognizer.AcceptWaveform(data)
    recognized_data = json.loads(offline_recognizer.Result())["text"]
    print(recognized_data)

    os.remove(wav_path)

    return recognized_data

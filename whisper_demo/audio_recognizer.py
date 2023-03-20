import whisper
import subprocess

model = whisper.load_model("base")


def recognize(file_name):
    mp3_path = "./" + file_name.split('.')[0] + ".mp3"
    # convert oog to wav
    command = f"ffmpeg -i {file_name} -ar 16000 -ac 1 -ab 256K -f mp3 {mp3_path}"
    _ = subprocess.check_call(command.split())

    recognizer_results = model.transcribe(f"./{mp3_path}")
    print(recognizer_results)

    return recognizer_results

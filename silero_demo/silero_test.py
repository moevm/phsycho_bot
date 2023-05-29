import torch
import time
import sounddevice as sd
import torchaudio

language = 'ru'
model_id = 'v3_1_ru'
sample_rate = 48000
speaker = 'aidar'
device = torch.device('cpu')
example_text = 'Привет я бот-психолог'


def silero_test(text=example_text):
    model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                         model='silero_tts',
                                         language=language,
                                         speaker=model_id)
    model.to(device)  # gpu or cpu

    audio = model.apply_tts(text=text,
                            speaker=speaker,
                            sample_rate=sample_rate)
    filename = 'test_1.wav'
    torchaudio.save(filename,
                    audio.unsqueeze(0),
                    sample_rate=sample_rate)
    return filename
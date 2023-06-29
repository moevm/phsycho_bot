import torch
import time
import sounddevice as sd
import torchaudio

language = 'ru'
model_id = 'v3_1_ru'
sample_rate = 48000
speaker = 'aidar'
device = torch.device('cpu')

def bot_answer_audio(bot_text):
    model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                         model='silero_tts',
                                         language=language,
                                         speaker=model_id)
    model.to(device)

    audio = model.apply_tts(text=bot_text,
                            speaker=speaker,
                            sample_rate=sample_rate)
    filename = 'test_1.wav'
    torchaudio.save(filename,
                    audio.unsqueeze(0),
                    sample_rate=sample_rate)
    return filename
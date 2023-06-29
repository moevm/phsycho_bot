import os
import torch
import time
import sounddevice as sd
import torchaudio


class SpeakerSettings:
    language = os.environ.get('LANGUAGE')
    model_id = os.environ.get('MODEL_ID')
    sample_rate = int(os.environ.get('SAMPLE_RATE'))
    speaker = os.environ.get('SPEAKER')


device = torch.device('cpu')


def bot_answer_audio(bot_text):
    model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                         model='silero_tts',
                                         language=SpeakerSettings.language,
                                         speaker=SpeakerSettings.model_id)
    model.to(device)

    audio = model.apply_tts(text=bot_text,
                            speaker=SpeakerSettings.speaker,
                            sample_rate=SpeakerSettings.sample_rate)
    filename = 'test_1.wav'
    torchaudio.save(filename,
                    audio.unsqueeze(0),
                    sample_rate=SpeakerSettings.sample_rate)
    return filename
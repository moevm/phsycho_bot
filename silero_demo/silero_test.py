import torch
import time
import sounddevice as sd
import torchaudio
import re

language = 'ru'
model_id = 'v3_1_ru'
sample_rate = 48000
speaker = 'aidar'
device = torch.device('cpu')
example_text = "Привет. я бот-психолог"

def add_intonation(text, words, intonation_parameters):
    text = text.lower()
    for word in words:
        text = text.replace(word, f"<{' '.join(intonation_parameters)}>" + word + f"</{intonation_parameters[0]}>")
    return text


def reformat_text(text):
    paragraphs = text.split('\n')
    for i in range(len(paragraphs)):
        sentences = ["<s>" + elem + "</s>" for elem in re.split(r'(?<=[.?!])\s+', paragraphs[i])]
        paragraphs[i] = '<p>' + ' '.join(sentences) + '</p>'
    text = "<speak>" + '\n'.join(paragraphs) + "</speak>"
    return text

def silero_test(text=example_text):
    model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                         model='silero_tts',
                                         language=language,
                                         speaker=model_id)
    model.to(device)  # gpu or cpu

    text = reformat_text(text)
    text = add_intonation(text, ["привет"], ['prosody', 'pitch="x-high"'])

    audio = model.apply_tts(ssml_text=text,
                            speaker=speaker,
                            sample_rate=sample_rate)
    filename = 'test_1.wav'
    torchaudio.save(filename,
                    audio.unsqueeze(0),
                    sample_rate=sample_rate)
    return filename
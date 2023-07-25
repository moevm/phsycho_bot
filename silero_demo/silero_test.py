import re

import torch
import torchaudio

LANGUAGE = 'ru'
MODEL_ID = 'v3_1_ru'
SAMPLE_RATE = 48000
SPEAKER = 'baya'
DEVICE = torch.device('cpu')
EXAMPLE_TEXT = "Привет. я бот-психолог"


def add_intonation(text, words, intonation_parameters):
    text = text.lower()
    for word in words:
        text = text.replace(
            word, f"<{' '.join(intonation_parameters)}>" + word + f"</{intonation_parameters[0]}>"
        )
    return text


def reformat_text(text):
    paragraphs = text.split('\n')
    for i in range(len(paragraphs)):
        sentences = ["<s>" + elem + "</s>" for elem in re.split(r'(?<=[.?!])\s+', paragraphs[i])]
        paragraphs[i] = '<p>' + ' '.join(sentences) + '</p>'
    text = "<speak>" + '\n'.join(paragraphs) + "</speak>"
    return text


def silero_test(text=EXAMPLE_TEXT):
    model, _ = torch.hub.load(
        repo_or_dir='snakers4/silero-models',
        model='silero_tts',
        language=LANGUAGE,
        speaker=MODEL_ID,
    )

    model.to(DEVICE)  # gpu or cpu

    text = reformat_text(text)
    text = add_intonation(text, ["привет"], ['prosody', 'pitch="x-high" rate="x-slow"'])
    text = add_intonation(text, ["пока"], ['prosody', 'pitch="x-low" rate="x-fast"'])

    audio = model.apply_tts(ssml_text=text, speaker=SPEAKER, sample_rate=SAMPLE_RATE)
    filename = 'test_1.wav'
    torchaudio.save(filename, audio.unsqueeze(0), sample_rate=SAMPLE_RATE)
    return filename

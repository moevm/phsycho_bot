import torch
from aniemore.recognizers.voice import VoiceRecognizer
from aniemore.models import HuggingFaceModel
from datasets import load_dataset
import soundfile as sf
import time
import os

# функция для получения .wav из датасета в файловую систему
def process_audio():
    dataset = load_dataset("Aniemore/resd")
    test_data = dataset['test']
    train_data = dataset['train']
    print(test_data.shape)
    for i in range(280):
        audio_data = test_data[i]['speech']
        print(audio_data)
        audio_array = audio_data['array']
        file_path = audio_data['path']
        sampling_rate = audio_data['sampling_rate']
        sf.write('test/' + file_path, audio_array, sampling_rate)

# функция распознавания эмоции по аудио
def recognize_audio(file_path, model_name):
    model = getattr(HuggingFaceModel.Voice, model_name)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    vr = VoiceRecognizer(model=model, device=device)
    result = vr.recognize(file_path, return_single_label=True)
    return result

# функция для сравнения результатов различных моделей
def recognize_many_models(file_path, models_to_recognize):
    results = []
    for model_name in models_to_recognize:
        start_time = time.time()
        result = recognize_audio(file_path, model_name)
        end_time = time.time()
        elapsed_time = end_time - start_time
        results.append(f"{model_name} result - {result}, Time: {elapsed_time:.4f} seconds")

    print(file_path)
    for item in results:
        print(item)


# получение списка файлов в папке
folder_path = 'test'
files_list = [os.path.join(folder_path, file) for file in os.listdir(folder_path)]

file_path = files_list[0]
models_to_recognize = [
    'WavLM',
    'Hubert',
    'UniSpeech',
    'Wav2Vec2'
]

recognize_many_models(file_path, models_to_recognize)

# примеры использования по моделей отдельности
#model_name = 'WavLM'
#print('WavLM')
#print(recognize_audio(file_path, model_name))

#model = HuggingFaceModel.Voice.Hubert
#print('Hubert')
#recognize_audio(file_path, model)

#model = HuggingFaceModel.Voice.UniSpeech
#print('Unispeech')
#recognize_audio(file_path, model)

#model = HuggingFaceModel.Voice.Wav2Vec2
#print('Wav2Vec2')
#recognize_audio(file_path, model)



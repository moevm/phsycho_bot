import speech_recognition as sr

def audio_to_text(file_path):
    recognizer = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)  # Записываем аудио из файла

    try:
        text = recognizer.recognize_google(audio_data, language="en-US")
        return text
    except sr.UnknownValueError:
        print("Речь не распознана")
    except sr.RequestError as e:
        print(f"Ошибка запроса к API: {e}")

# Пример использования
file_path = "C:\\Users\\yarkr\\Desktop\\CREMA-D\\AudioWAV\\1001_DFA_ANG_XX.wav"
text = audio_to_text(file_path)
print(f"Text: {text}")
# data_path = "C:\\Users\\yarkr\\Desktop\\CREMA-D\\AudioWAV"
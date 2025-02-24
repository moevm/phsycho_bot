import os
import sys
from string import punctuation
from collections import Counter
import nltk
from nltk.corpus import stopwords
from pymystem3 import Mystem

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'emotion_recognition')))

from emotion_recognition.source.audio_analysis_utils.predict import predict


def get_words_statistics(text: str):
    nltk.download('stopwords')
    mystem = Mystem()

    tokens = mystem.lemmatize(text.lower())
    stop_words = set(stopwords.words('russian'))
    tokens = list(filter(lambda token: token not in stop_words and token.strip() not in punctuation, tokens))

    return dict(Counter(tokens))


def predict_emotion(filename):
    emotion, predicted_label, prediction_string = predict(filename)
    return emotion


def associate_words_with_emotions(filename, speech_text):
    words_statistics = get_words_statistics(speech_text)
    predicted_emotion = predict_emotion(filename)
    return max(words_statistics, key=words_statistics.get), predicted_emotion

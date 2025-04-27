from string import punctuation
from collections import Counter
import nltk
from nltk.corpus import stopwords
from pymystem3 import Mystem
from emotion_recognition.source.face_emotion_utils.predict import predict  # pylint: disable=import-error


def predict_emotion(filename):
    print("PREDICT EMOTION")
    result = predict(filename, video_mode=True, target_fps=2)
    emotions = [frame_result[0] for frame_result in result]
    return max(emotions, key=emotions.count)


def get_words_statistics(text: str):
    nltk.download('stopwords')
    mystem = Mystem()

    tokens = mystem.lemmatize(text.lower())
    stop_words = set(stopwords.words('russian'))
    tokens = list(filter(lambda token: token not in stop_words and token.strip() not in punctuation, tokens))

    return dict(Counter(tokens))

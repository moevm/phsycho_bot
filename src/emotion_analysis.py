import os
import sys
from string import punctuation
from collections import Counter
import nltk
from nltk.corpus import stopwords
from pymystem3 import Mystem

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'emotion_recognition')))

from emotion_recognition.source.face_emotion_utils.predict import predict
from emotion_recognition.source.face_emotion_utils.utils import find_filename_match



def predict_emotion(filename):
    print("PREDICT EMOTION")
    result = predict(filename, video_mode=True, target_fps=2)
    emotions = [frame_result[0] for frame_result in result]
    return max(emotions, key=emotions.count)

from emotion_recognition.source.face_emotion_utils.predict import predict  # pylint: disable=import-error


def predict_emotion(filename):
    print("PREDICT EMOTION")
    result = predict(filename, video_mode=True, target_fps=2)
    emotions = [frame_result[0] for frame_result in result]
    return max(emotions, key=emotions.count)

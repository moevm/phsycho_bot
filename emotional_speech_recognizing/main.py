import os
import time
import numpy as np

import librosa
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import EarlyStopping

start_time = time.time()

# Путь к папке с датасетом
DATASET_DIR = r'AudioData'

# Список эмоций и соответствующих меток
emotions = {'a': 0, 'd': 1, 'f': 2, 'h': 3, 'n': 4, 'sa': 5, 'su': 6}

# Списки для хранения признаков и меток
X = []
y = []

# Проход по каждой эмоции в папке датасета
for emotion in emotions.keys():
    # Путь к папке с эмоцией
    emotion_dir = os.path.join(DATASET_DIR, emotion)

    # Проход по каждому аудиофайлу в папке с эмоцией
    for file in os.listdir(emotion_dir):
        audio_path = os.path.join(emotion_dir, file)

        # Загрузка аудиозаписи и извлечение признаков с помощью librosa
        waveform, sample_rate = librosa.load(audio_path, duration=6, offset=0)
        mfccs = librosa.feature.mfcc(y=waveform, sr=sample_rate, n_mfcc=100)
        mfccs_processed = np.mean(mfccs.T, axis=0)

        X.append(mfccs_processed)
        y.append(emotions[emotion])

# Преобразование списков в массивы numpy
X = np.array(X)
y = np.array(y)

# Разделение на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Создание модели нейронной сети
model = Sequential()
model.add(Dense(100, activation='relu', input_shape=(X_train.shape[1],)))
# model.add(Dropout(0.5))
model.add(Dense(100, activation='relu'))
# model.add(Dense(15, activation='relu'))
# model.add(Dense(120, activation='relu'))
# model.add(Dropout(0.5))
model.add(Dense(len(emotions), activation='softmax'))

# Компиляция модели
# model.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])
model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Обучение модели
early_stopping = EarlyStopping(monitor='val_loss', patience=10)
model.fit(X_train, y_train, epochs=50, batch_size=1, validation_data=(X_test, y_test), callbacks=[early_stopping])

# Оценка модели на тестовой выборке
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
end_time = time.time()
runtime = end_time - start_time
print(f"Program runtime: {runtime:.2f} seconds")
print(f'Test Loss: {loss:.4f}')
print(f'Test Accuracy: {accuracy * 100:.2f}%')

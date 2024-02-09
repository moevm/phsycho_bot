import os
import librosa
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt

# Путь к папке с аудиозаписями
data_path = "/app/CREMA-D/AudioWAV"

# Извлечение признаков из аудиозаписи
def extract_features(file_path):
    audio, sample_rate = librosa.load(file_path, res_type='kaiser_fast')
    mfccs = np.mean(librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13), axis=1)
    chroma = np.mean(librosa.feature.chroma_stft(y=audio, sr=sample_rate), axis=1)
    mel = np.mean(librosa.feature.melspectrogram(y=audio, sr=sample_rate), axis=1)
    return np.concatenate((mfccs, chroma, mel))

# Создание массивов для данных и меток
X = []
y = []

# Извлечение признаков из каждой аудиозаписи
for file_name in os.listdir(data_path):
    if file_name.endswith(".wav"):
        file_path = os.path.join(data_path, file_name)
        features = extract_features(file_path)
        X.append(features)
        y.append(1 if "ANG" in file_name or "SAD" in file_name else 0)

# Преобразование в массив NumPy
X = np.array(X)
y = np.array(y)

# Разделение данных на обучающий и тестовый наборы
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Нормализация данных
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Изменение формы данных для LSTM
X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

# Создание и компиляция модели LSTM
model = Sequential()
model.add(LSTM(100, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Обучение модели
history = model.fit(X_train, y_train, epochs=20, batch_size=64, validation_data=(X_test, y_test), verbose=1)

# Предсказание на тестовом наборе
y_pred_prob = model.predict(X_test)
y_pred = (y_pred_prob > 0.5).astype(int)

# Оценка модели
accuracy = accuracy_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

model.save('model-audio.h5')

# Вывод результатов
print(f"Accuracy: {accuracy}")
print("Confusion Matrix:")
print(conf_matrix)

# Визуализация матрицы ошибок
plt.imshow(conf_matrix, interpolation='nearest', cmap=plt.cm.Blues)
plt.title('Confusion Matrix')
plt.colorbar()
plt.xticks([0, 1], ['No Stress', 'Stress'])
plt.yticks([0, 1], ['No Stress', 'Stress'])
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.show()
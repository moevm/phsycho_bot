import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Загрузка данных
train_data_text = pd.read_csv('../app/archive/emotion-labels-train.csv')
val_data_text = pd.read_csv('../app/archive/emotion-labels-val.csv')
test_data_text = pd.read_csv('../app/archive/emotion-labels-test.csv')

# Фильтрация текстовых данных для включения всех меток
all_labels = ['fear', 'anger', 'joy', 'sadness']
train_data_text = train_data_text[train_data_text['label'].isin(all_labels)]
val_data_text = val_data_text[val_data_text['label'].isin(all_labels)]
test_data_text = test_data_text[test_data_text['label'].isin(all_labels)]

# Преобразование меток текстовых данных в числовые значения: 1 - стресс, 0 - не стресс
label_mapping = {'fear': 1, 'anger': 1, 'joy': 0, 'sadness': 0}
for dataset in [train_data_text, val_data_text, test_data_text]:
    dataset['label'] = dataset['label'].map(label_mapping)


# Предварительная обработка текста и меток
vectorizer = TfidfVectorizer(max_features=1000)
X_train = vectorizer.fit_transform(train_data_text['text'])
y_train = train_data_text['label']

X_val = vectorizer.transform(val_data_text['text'])
y_val = val_data_text['label']

X_test = vectorizer.transform(test_data_text['text'])
y_test = test_data_text['label']
print(train_data_text['label'].unique())

# Создание и обучение модели
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

joblib.dump(model, 'model-text.pkl')
# Предсказание на валидационной выборке
val_predictions = model.predict(X_val)

# Оценка производительности модели на валидационной выборке
accuracy = accuracy_score(y_val, val_predictions)
print(f'Accuracy on validation set: {accuracy:.2f}')

# Отчет по классификации на валидационной выборке
print(classification_report(y_val, val_predictions))

# Оценка производительности модели на тестовой выборке
test_predictions = model.predict(X_test)
test_accuracy = accuracy_score(y_test, test_predictions)
print(f'Accuracy on test set: {test_accuracy:.2f}')

# Отчет по классификации на тестовой выборке
print(classification_report(y_test, test_predictions))

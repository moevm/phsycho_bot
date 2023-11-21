# Распознавание стресса по голосу

Модели для расспознавания стресса по голосу и тексту.

## Установка

1. Клонируйте репозиторий: `git clone https://github.com/moevm/phsycho_bot.git`
2. Перейдите в каталог playground/modelstress
3. Команды для запуска модели распознавания стресса по тексту: `docker build -t text_model -f Dockerfile-text .`,`docker run -v ваш_путь/archive:/app/archive text_model`
4. Команды для запуска модели распознавания стресса по голосу: `docker build -t audio_model -f Dockerfile-audio .`, `docker run -v ваш_путь/CREMA-D/AudioWAV:/app/CREMA-D/AudioWAV audio_model`
5. Замените путь в командах с ваш_путь на текущиее расположение файлов


docker build -t text_model -f Dockerfile-text .
docker build -t audio_model -f Dockerfile-audio .

docker run -v C:/Users/yarkr/Desktop/diplom/archive:/app/archive text_model
docker run -v C:/Users/yarkr/Desktop/diplom/CREMA-D/AudioWAV:/app/CREMA-D/AudioWAV audio_model
FROM python:3.10



RUN apt-get update && apt-get install -y ffmpeg && apt-get install -y espeak

ENV RUVERSION 0.22
WORKDIR /bot
RUN mkdir model && wget -q http://alphacephei.com/kaldi/models/vosk-model-small-ru-${RUVERSION}.zip \
   && unzip vosk-model-small-ru-${RUVERSION}.zip \
   && mv vosk-model-small-ru-${RUVERSION} model \
   && rm -rf model/extra \
   && rm -rf vosk-model-small-ru-${RUVERSION}.zip

COPY ./requirements.txt /bot/
RUN pip3 install -r requirements.txt

COPY . /bot/


ARG TELEGRAM_TOKEN

CMD python ./bot.py ${TELEGRAM_TOKEN} ${MONGO_INITDB_ROOT_USERNAME} ${MONGO_INITDB_ROOT_PASSWORD} ${MODE}

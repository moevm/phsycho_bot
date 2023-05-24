FROM python:3.8

WORKDIR /bot

RUN apt-get update && apt-get install -y ffmpeg && apt-get install -y espeak

ENV RUVERSION 0.22
RUN mkdir model && wget -q http://alphacephei.com/kaldi/models/vosk-model-small-ru-${RUVERSION}.zip \
   && unzip vosk-model-small-ru-${RUVERSION}.zip \
   && mv vosk-model-small-ru-${RUVERSION} model \
   && rm -rf model/extra \
   && rm -rf vosk-model-small-ru-${RUVERSION}.zip
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
ARG TOKEN

CMD python ./bot.py ${TOKEN} ${MONGODB_USERNAME} ${MONGODB_PASSWORD} ${MODE}
FROM python:3.8

WORKDIR /bot

RUN apt-get update
RUN apt-get install -y ffmpeg libportaudio2

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .


ARG TOKEN

CMD python ./bot.py ${TOKEN}
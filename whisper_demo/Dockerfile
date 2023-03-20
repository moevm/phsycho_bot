FROM python:3.8

WORKDIR /bot

COPY . .

RUN apt-get update
RUN apt-get install -y ffmpeg
RUN pip3 install -r requirements.txt

ARG TOKEN

CMD python ./bot.py ${TOKEN}
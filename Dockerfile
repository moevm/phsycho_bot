FROM python:3.10


RUN apt-get update && apt-get install -y ffmpeg="7:5.1.4-0+deb12u1" && apt-get install -y espeak="1.48.15+dfsg-3"

ENV RUVERSION 0.22
WORKDIR /bot

COPY src/requirements.txt src/
RUN pip3 install -r src/requirements.txt

# COPY tests/requirements.txt tests/
# RUN pip3 install -r tests/requirements.txt

COPY . /bot/

ENV TZ 'Europe/Moscow'
RUN echo $TZ > /etc/timezone && \
    apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata


ARG TELEGRAM_TOKEN

CMD python src/bot.py ${TELEGRAM_TOKEN} ${MONGO_INITDB_ROOT_USERNAME} ${MONGO_INITDB_ROOT_PASSWORD}

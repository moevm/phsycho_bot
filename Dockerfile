    FROM python:3.10 AS base

    ARG TELEGRAM_TOKEN

    ENV RUVERSION 0.22
    ENV TZ 'Europe/Moscow'

    RUN apt-get update && \
        DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-downgrades\
        ffmpeg="7:5.1.6-0+deb12u1" \
        espeak="1.48.15+dfsg-3" \
        libsm6="2:1.2.3-1" \
        libxext6="2:1.3.4-1+b1" \
        git="1:2.39.5-0+deb12u2"  \
        tzdata="2025b-0+deb12u1" && \
        apt-get clean

    RUN echo $TZ > /etc/timezone && \
        rm /etc/localtime && \
        ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
        dpkg-reconfigure -f noninteractive tzdata


    FROM base AS emotion_recognition

    RUN pip3 install --no-cache-dir \
        torch==1.13.1+cu117 \
        torchvision>=0.13.1+cu117 \
        torchaudio>=0.13.1+cu117 --extra-index-url https://download.pytorch.org/whl/cu117

    WORKDIR /bot/emotion_recognition

    RUN git clone https://github.com/elizaveta-andreeva/Video-Audio-Face-Emotion-Recognition.git . && \
        git checkout 9b3368ccdce1d571a362543633ade81eb0cbd622

    RUN git clone https://github.com/rishiswethan/pytorch_utils.git source/pytorch_utils && \
        cd source/pytorch_utils && \
        git checkout v1.0.3 && \
        cd ../.. && \
        python3 setup.py

    RUN pip3 install --no-cache-dir -r requirements.txt
    RUN python3 -m spacy download en_core_web_lg


    FROM emotion_recognition AS phsycho_bot

    WORKDIR /bot

    COPY src/requirements.txt src/
    RUN pip3 install --no-cache-dir -r src/requirements.txt

    # COPY tests/requirements.txt tests/
    # RUN pip3 install -r tests/requirements.txt

    COPY . /bot/

    ENV PYTHONPATH="/bot:/bot/emotion_recognition:${PYTHONPATH}"

    CMD python3 src/bot.py ${TELEGRAM_TOKEN} ${MONGO_INITDB_ROOT_USERNAME} ${MONGO_INITDB_ROOT_PASSWORD}
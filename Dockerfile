FROM python:3.8

WORKDIR /bot

COPY * /bot/

RUN pip3 install -r requirements.txt

ARG TOKEN

CMD python ./bot.py ${TOKEN} ${MONGODB_USERNAME} ${MONGODB_PASSWORD}

FROM python:3.8
#set workdirectory
WORKDIR /bot

COPY * /bot/
#COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ARG TOKEN

CMD ["python", "./bot.py", "${TOKEN}"]

CMD python ./bot.py ${TOKEN} ${MONGODB_HOST}
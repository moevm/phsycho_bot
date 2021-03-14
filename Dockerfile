FROM python:3
#set workdirectory
WORKDIR /bot

COPY * /bot/
#COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt


CMD ["python", "./bot.py"]
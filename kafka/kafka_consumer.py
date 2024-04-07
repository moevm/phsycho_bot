import os

from confluent_kafka import Consumer
from telegram import User, Bot, Update
import json

from kafka import kafka_operations
from voice_module import audio_to_text


def process_stt_message(message_info):
    message_info = json.loads(message_info)
    user = User(**message_info['user'])
    audio_to_text(message_info['token'], message_info['filename'], message_info['ogg_filename'],
                  message_info['update_id'], user)


def main():
    print(os.getcwd(), os.listdir())
    conf = kafka_operations.load_conf('kafka/consumer_conf.json')
    consumer = Consumer(conf)
    consumer.subscribe(['stt'])

    while True:
        message = consumer.poll(0)

        if message is None:
            continue
        if message.error():
            print("Consumer error happened: {}".format(message.error()))
            continue

        # print("Connected to Topic: {} and Partition : {}".format(message.topic(), message.partition()))
        # print("Received Message : {} with Offset : {}".format(message.value().decode('utf-8'), message.offset()))
        process_stt_message(message.value().decode('utf-8'))

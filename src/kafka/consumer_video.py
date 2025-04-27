import json

from confluent_kafka import Consumer
from telegram import User
from kafka import kafka_operations
from modules.video.video_module import process_video


def process_stt_message(message_info):
    message_info = json.loads(message_info)
    user = User(**message_info['user'])
    process_video(message_info['video_path'], message_info['emotion_dir_video_path'], message_info['update_id'], user)


def main():
    conf = kafka_operations.load_conf('src/kafka/consumer_video_conf.json')
    consumer = Consumer(conf)
    consumer.subscribe(['video'])

    while True:
        message = consumer.poll(0)

        if message is None:
            continue
        if message.error():
            print(f"Consumer error happened: {message.error()}")
            continue

        # print("Connected to Topic: {} and Partition : {}".format(message.topic(), message.partition()))
        # print("Received Message : {} with Offset : {}".format(message.value().decode('utf-8'), message.offset()))
        process_stt_message(message.value().decode('utf-8'))

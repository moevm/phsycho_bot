import json
from confluent_kafka import Consumer
from telegram import User


from kafka import kafka_operations
from utilities.wrapper import send_voice

conf = kafka_operations.load_conf('src/kafka/consumer_tts_conf.json')


def process_tts_message(message_info):
    message_info = json.loads(message_info)
    user = User(**message_info['user'])
    send_voice(message_info['text'], user, message_info['reply_markup'])


def main():
    consumer = Consumer(conf)
    consumer.subscribe(['tts'])
    while True:
        message = consumer.poll(0)

        if message is None:
            continue
        if message.error():
            print(f"Consumer error happened: {message.error()}")
            continue

        # print("Connected to Topic: {} and Partition : {}".format(message.topic(), message.partition()))
        # print("Received Message : {} with Offset : {}".format(message.value().decode('utf-8'), message.offset()))
        process_tts_message(message.value().decode('utf-8'))

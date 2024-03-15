from confluent_kafka import Consumer
from telegram.ext import Updater

conf = {
    'bootstrap.servers': 'kafka:29092',
    'group.id': 'Psycho-bot',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True,
}


def main():
    consumer = Consumer(conf)
    consumer.subscribe(['stt'])

    while True:
        message = consumer.poll(0)

        if message is None:
            continue
        if message.error():
            print("Consumer error happened: {}".format(message.error()))
            continue

        print("Connected to Topic: {} and Partition : {}".format(message.topic(), message.partition()))
        print("Received Message : {} with Offset : {}".format(message.value().decode('utf-8'), message.offset()))

        # time.sleep(2.5)

from confluent_kafka import Producer
from uuid import uuid4


conf = {
    'bootstrap.servers': 'kafka:29092'
}

def delivery_report(errmsg, msg):
    if errmsg is not None:
        print("Delivery failed for Message: {} : {}".format(msg.key(), errmsg))
        return
    print('Message: {} successfully produced to Topic: {} Partition: [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))

def produce_message(topic, message):
    producer = Producer(conf)
    producer.poll(0)
    try:
        producer.produce(topic=topic, key=str(uuid4()), value=message, on_delivery=delivery_report)
        producer.flush()
    except Exception as ex:
        print("Exception happened :", ex)


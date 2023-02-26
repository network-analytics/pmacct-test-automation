
#from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka.avro import AvroConsumer
import time

def get_next_message(topic, seconds):
    consumer = AvroConsumer({
        'bootstrap.servers': 'localhost:9092',
        'schema.registry.url': 'http://localhost:8081',
        'security.protocol': 'PLAINTEXT',
        'group.id': 'smoke_test',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe([topic])
    msg = consumer.poll(seconds)
    consumer.close()
    if msg is None:
        print('No messages read by kafka consumer in ' + str(seconds) + ' seconds - ', end='')
        return None
    if msg.error():
        print("Kafka consumer error: " + str(msg.error()))
        return None
    print('Received following data from pmacct through Kafka: ' + str(msg.value()))
    print('Received ' + str(msg.value()["packets"]) + ' IPFIX packets')
    return msg


def check_packets_in_kafka_message(topic):
    tries = 20
    message = get_next_message(topic, 5)
    while not message:
        tries -= 1
        if tries<1:
            print('Kafka consumer timed out')
            return None
        print('Retrying... ')
        time.sleep(10)
        message = get_next_message(topic, 5)
    #while message: ... need to handle multiple messages here
    packet_count = int(message.value()["packets"])
    message_timestamp = int(message.timestamp()[1])
    return (packet_count, message_timestamp)
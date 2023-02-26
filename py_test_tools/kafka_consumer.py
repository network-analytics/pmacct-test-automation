
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
        return -1
    if msg.error():
        print("Kafka consumer error: " + str(msg.error()))
        return -1
    print('Received following data from pmacct through Kafka: ' + str(msg.value()))
    print('Received ' + str(msg.value()["packets"]) + ' IPFIX packets')
    num_packets = msg.value()["packets"]
    return num_packets


def check_kafka_packets(topic):
    tries = 20
    packet_count = get_next_message(topic, 5)
    while packet_count<0:
        tries -= 1
        if tries<1:
            print('Kafka consumer timed out')
            return -1
        print('Retrying... ')
        time.sleep(10)
        packet_count = get_next_message(topic, 5)
    return packet_count
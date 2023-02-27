
#from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka.avro import AvroConsumer
import time


def get_all_messages(topic, max_time_seconds, packets_expected):
    consumer = AvroConsumer({
        'bootstrap.servers': 'localhost:9092',
        'schema.registry.url': 'http://localhost:8081',
        'security.protocol': 'PLAINTEXT',
        'group.id': 'smoke_test',
        'auto.offset.reset': 'earliest'
    })
    messages = []
    consumer.subscribe([topic])
    time_start = round(time.time())
    time_now = round(time.time())
    while packets_expected>0 and time_now-time_start<max_time_seconds:
        msg = consumer.poll(5)
        if not msg or msg.error():
            print('No msg or msg error, sleeping (' + str(max_time_seconds-time_now+time_start) + ' seconds left)')
            #time.sleep(2)
        else:
            print('Received: ' + str(msg.value()))
            messages.append(msg)
            packets_expected -= int(msg.value()["packets"])
            if packets_expected>0:
                print('Waiting for ' + str(packets_expected) + ' packets to be reported')
        time_now = round(time.time())
    consumer.close()
    if packets_expected<1:
        print('All sent packets reported')
    if len(messages)<1:
        print('No messages read by kafka consumer in ' + str(max_time_seconds) + ' seconds - ', end='')
        return None
    return messages


def check_packets_in_kafka_message(topic, packets_expected):
    tries = 20
    messages = get_all_messages(topic, 120, packets_expected)
    if not messages:
        print('Kafka consumer timed out')
        return None
    print('Received following data from pmacct through Kafka: ')
    packet_count = 0
    for msg in messages:
        packet_count += int(msg.value()["packets"])
        print(str(msg.value()))
    message_timestamp = int(messages[0].timestamp()[1])
    print('Pmacct processed ' + str(packet_count) + ' packets')
    return (packet_count, message_timestamp)

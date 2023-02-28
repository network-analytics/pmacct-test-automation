###################################################
# Automated Testing Framework for Network Analytics
#
# functions for Kafka consumption
#
###################################################

#from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka import cimpl
import time
from typing import List

# Reads all messages currently available in Kafka topic
# topic: Kafka topic name to read messages from
# packets_expected: number of packets expected to be reported by pmacct. If the sum of packets reported
#    in the messages reaches this number, the message reading process is stopped and messages are returned
# max_time_seconds: maximum time in seconds, in which the expected number of packets needs to be reported. If
#    the time is reached without all packets having been reported, the messages read so far are returned
def get_all_messages(topic: str, max_time_seconds: int, packets_expected: int) -> List[cimpl.Message]:
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


# Returns the total number of packets reported by pmacct in the queued Kafka messages
# It uses get_all_messages function and a max waiting time of 120 seconds
# topic: Kafka topic name to read messages from
# packets_expected: number of packets expected to be reported by pmacct. If equal or more packets are reported,
#    process stops. Also, if time exceeds 120 seconds, the process stops.
def check_packets_in_kafka_message(topic: str, packets_expected: int) -> (int, int):
    tries = 20
    messages = get_all_messages(topic, 120, packets_expected)
    if not messages:
        print('Kafka consumer timed out')
        return None
    #print('Received following data from pmacct through Kafka: ')
    packet_count = 0
    for msg in messages:
        packet_count += int(msg.value()["packets"])
        #print(str(msg.value()))
    message_timestamp = int(messages[0].timestamp()[1])
    print('Pmacct processed ' + str(packet_count) + ' packets')
    return (packet_count, message_timestamp)

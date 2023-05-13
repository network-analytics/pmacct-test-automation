###################################################
# Automated Testing Framework for Network Analytics
#
# functions for Kafka consumption
#
###################################################

#from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka import cimpl
import time, logging
from typing import List
logger = logging.getLogger(__name__)

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
            logger.debug('No msg or msg error, sleeping (' + str(max_time_seconds-time_now+time_start) + ' seconds left)')
        else:
            packets_received = int(msg.value()["packets"])
            logger.info('Received: ' + str(packets_received) + ' packets')
            logger.debug('Received message: ' + str(msg.value()))
            messages.append(msg)
            packets_expected -= packets_received
            if packets_expected>0:
                logger.info('Waiting for ' + str(packets_expected) + ' more packets to be reported')
        time_now = round(time.time())
    consumer.close()
    if packets_expected<1:
        logger.info('All sent packets reported')
    if len(messages)<1:
        logger.info('No messages read by kafka consumer in ' + str(max_time_seconds) + ' second(s)')
        return None
    return messages


# Returns the total number of packets reported by pmacct in the queued Kafka messages, along
# with the timestamp of the first message read and the whole last message
# It uses get_all_messages function and a max waiting time of 120 seconds
# topic: Kafka topic name to read messages from
# packets_expected: number of packets expected to be reported by pmacct. If equal or more packets are reported,
#    process stops. Also, if time exceeds 120 seconds, the process stops.
# max_time: time to wait for messages to come (default 120)
def check_packets_in_kafka_message(topic: str, packets_expected: int, max_time: int =120) -> (int, int):
    messages = get_all_messages(topic, max_time, packets_expected)
    if not messages:
        logger.info('Kafka consumer timed out')
        return None
    packet_count = 0
    for msg in messages:
        packet_count += int(msg.value()["packets"])
    message_timestamp = int(messages[0].timestamp()[1])
    logger.info('Pmacct processed ' + str(packet_count) + ' packets')
    last_message = messages[-1].value()
    return (packet_count, message_timestamp, last_message)

# Returns the total number of packets reported by pmacct in the queued Kafka messages, along
# with the value of the key peer_ip_src of the first message read
# It uses get_all_messages function and a max waiting time of 120 seconds
# topic: Kafka topic name to read messages from
# packets_expected: number of packets expected to be reported by pmacct. If equal or more packets are reported,
#    process stops. Also, if time exceeds 120 seconds, the process stops.
# max_time: time to wait for messages to come (default 120)
def check_packets_and_get_IP(topic: str, packets_expected: int, max_time: int =120) -> (int, int):
    messages = get_all_messages(topic, max_time, packets_expected)
    if not messages:
        logger.info('Kafka consumer timed out')
        return None
    packet_count = 0
    for msg in messages:
        packet_count += int(msg.value()["packets"])
    logger.info('Pmacct processed ' + str(packet_count) + ' packets')
    peer_ip = str(messages[0].value()["peer_ip_src"])
    logger.info('Peer src ip: ' + peer_ip)
    return (packet_count, peer_ip)

def get_messages(topic: str, max_time_seconds: int, messages_expected: int) -> List[cimpl.Message]:
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
    while messages_expected>0 and time_now-time_start<max_time_seconds:
        msg = consumer.poll(5)
        if not msg or msg.error():
            logger.debug('No msg or msg error, sleeping (' + str(max_time_seconds-time_now+time_start) + ' seconds left)')
        else:
            logger.debug('Received message: ' + str(msg.value()))
            messages.append(msg)
            messages_expected -= 1
            if messages_expected>0:
                logger.info('Waiting for ' + str(messages_expected) + ' more messages')
        time_now = round(time.time())
    consumer.close()
    if messages_expected<1:
        logger.info('All expected messages received')
    if len(messages)<1:
        logger.info('No messages read by kafka consumer in ' + str(max_time_seconds) + ' second(s)')
        return None
    return messages
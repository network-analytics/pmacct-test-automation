###################################################
# Automated Testing Framework for Network Analytics
#
# functions for Kafka consumption
#
###################################################

from confluent_kafka.avro import AvroConsumer
from confluent_kafka import cimpl
import time, logging, json
from typing import List
logger = logging.getLogger(__name__)

class KMessageReader:

    def __init__(self, topic, dump_to_file=None):
        self.topic = topic
        self.dumpfile = dump_to_file
        self.consumer = None

    def connect(self):
        self.consumer = AvroConsumer({
            'bootstrap.servers': 'localhost:9092',
            'schema.registry.url': 'http://localhost:8081',
            'security.protocol': 'PLAINTEXT',
            'group.id': 'smoke_test',
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe([self.topic])

    def disconnect(self):
        logger.debug('Message reader disconnect called')
        if self.consumer:
            logger.debug('Consumer exists')
            self.consumer.close()
            logger.debug('Consumer closed')

    def __del__(self):
        logger.debug('Message reader destructor called')
        if self.consumer:
            logger.debug('Consumer exists')
            self.consumer.close()
            logger.debug('Consumer closed')


    def dump_if_needed(self, msg):
        if not self.dumpfile:
            return
        with open(self.dumpfile, 'a') as f:
            f.write(json.dumps(msg.value()) + '\n')

    # Reads all messages currently available in Kafka topic
    # topic: Kafka topic name to read messages from
    # packets_expected: number of packets expected to be reported by pmacct. If the sum of packets reported
    #    in the messages reaches this number, the message reading process is stopped and messages are returned
    # max_time_seconds: maximum time in seconds, in which the expected number of packets needs to be reported. If
    #    the time is reached without all packets having been reported, the messages read so far are returned
    def get_all_messages(self, max_time_seconds: int, packets_expected: int) -> List[cimpl.Message]:
        messages = []
        time_start = round(time.time())
        time_now = round(time.time())
        while packets_expected>0 and time_now-time_start<max_time_seconds:
            msg = self.consumer.poll(5)
            if not msg or msg.error():
                logger.debug('No msg or msg error, sleeping (' + str(max_time_seconds-time_now+time_start) + ' seconds left)')
            else:
                self.dump_if_needed(msg)
                packets_received = int(msg.value()["packets"])
                logger.info('Received: ' + str(packets_received) + ' packets')
                logger.debug('Received message: ' + str(msg.value()))
                messages.append(msg)
                packets_expected -= packets_received
                if packets_expected>0:
                    logger.info('Waiting for ' + str(packets_expected) + ' more packets to be reported')
            time_now = round(time.time())
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
    def check_packets_in_kafka_message(self, packets_expected: int, max_time: int =120) -> (int, int):
        messages = self.get_all_messages(max_time, packets_expected)
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
    def check_packets_and_get_IP(self, packets_expected: int, max_time: int =120) -> (int, int):
        messages = self.get_all_messages(max_time, packets_expected)
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

    def get_messages(self, max_time_seconds: int, messages_expected: int) -> List[cimpl.Message]:
        messages = []
        message_count = messages_expected
        time_start = round(time.time())
        time_now = round(time.time())
        while messages_expected>0 and time_now-time_start<max_time_seconds:
            msg = self.consumer.poll(5)
            if not msg or msg.error():
                logger.debug('No msg or msg error, sleeping (' + str(max_time_seconds-time_now+time_start) + ' seconds left)')
            else:
                self.dump_if_needed(msg)
                logger.debug('Received message: ' + str(msg.value()))
                messages.append(msg)
                messages_expected -= 1
                if messages_expected>0:
                    logger.info('Waiting for ' + str(messages_expected) + ' more messages')
            time_now = round(time.time())
        if messages_expected<1:
            logger.info('Received the expected number of messages (' + str(message_count) + ')')
        if len(messages)<1:
            logger.info('No messages read by kafka consumer in ' + str(max_time_seconds) + ' second(s)')
            return None
        return messages
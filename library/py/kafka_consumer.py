###################################################
# Automated Testing Framework for Network Analytics
# Classes for Kafka consumption
# nikolaos.tsokas@swisscom.com 21/02/2023
###################################################

from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka import Consumer
import time, logging, json
from typing import List
from abc import ABC, abstractmethod
logger = logging.getLogger(__name__)

class KMessageReader(ABC):

    def __init__(self, topic: str, dump_to_file: str=None):
        self.topic = topic
        self.dumpfile = dump_to_file
        self.consumer = None

    @abstractmethod
    def instantiate_consumer(self, prop_dict):
        raise NotImplementedError("Must override instantiate_consumer")

    @abstractmethod
    def get_json_string_and_dict(self, message):
        raise NotImplementedError("Must override get_json_string_and_dict")

    def connect(self):
        prop_dict = {
                'bootstrap.servers': 'localhost:9092',
                'security.protocol': 'PLAINTEXT',
                'group.id': 'smoke_test',
                'auto.offset.reset': 'earliest'
            }
        self.instantiate_consumer(prop_dict)
        self.consumer.subscribe([self.topic])

    def disconnect(self):
        logger.debug('Message reader disconnect called')
        if self.consumer:
            logger.debug('Consumer exists')
            self.consumer.close()
            logger.debug('Consumer closed')
            self.consumer = None
        else:
            logger.debug('Consumer is already down')

    def __del__(self):
        logger.debug('Message reader destructor called')
        self.disconnect()

    def dump_json_if_needed(self, msgval: str):
        if not self.dumpfile:
            return
        with open(self.dumpfile + '.json', 'a') as f:
            f.write(msgval + '\n')

    def dump_raw_if_needed(self, msgval):
        if not self.dumpfile:
            return
        with open(self.dumpfile + '.dat', 'ab') as f:
            f.write(msgval)
        with open(self.dumpfile + '.txt', 'a') as f:
            f.write(str(msgval) + '\n')


    # Receives as input the maximum time to wait and the number of expected messages
    # Returns a list of dictionaries representing the messages received, or None if fewer than expected messages
    # (or no messages at all) were received
    def get_messages(self, max_time_seconds: int, messages_expected: int) -> List[dict]:
        messages = []
        message_count = messages_expected
        time_start = round(time.time())
        time_now = round(time.time())
        while messages_expected>0 and time_now-time_start<max_time_seconds:
            try:
                msg = self.consumer.poll(5)
            except Exception as err:
                logger.error(str(err))
                return messages
            if not msg:
                logger.debug('No message received from Kafka, waiting (' + str(max_time_seconds-time_now+time_start) +
                    ' seconds left)')
            elif msg.error():
                logger.warning('Erroneous message received from Kafka, waiting (' + str(max_time_seconds - time_now +
                    time_start) + ' seconds left)')
            else:
                self.dump_raw_if_needed(msg.value())
                msgval, msgdict = self.get_json_string_and_dict(msg)
                self.dump_json_if_needed(msgval)
                logger.debug('Received message: ' + msgval)
                messages.append(msgdict)
                messages_expected -= 1
                if messages_expected>0:
                    logger.debug('Waiting for ' + str(messages_expected) + ' more messages')
            time_now = round(time.time())
        if messages_expected<1:
            logger.info('Received the expected number of messages (' + str(message_count) + ')')
        if len(messages)<1:
            logger.warning('No messages read by kafka consumer in ' + str(max_time_seconds) + ' second(s)')
            return None
        if len(messages)<message_count:
            logger.warning('Received ' + str(len(messages)) + ' messages instead of ' + str(message_count))
            return None
        return messages

    # Returns all available (pending) messages in the Kafka topic. Messages are returned as dictionaries.
    def get_all_messages(self, maxcount = -1) -> List[dict]:
        messages = []
        msg = self.consumer.poll(5)
        while msg and not msg.error() and (maxcount<0 or len(messages)<maxcount):
            _, json_dict = self.get_json_string_and_dict(msg)
            messages.append(json_dict)
            msg = self.consumer.poll(5)
        return messages


class KMessageReaderAvro(KMessageReader):

    def __init__(self, topic: str, dump_to_file: str=None):
        logger.info('Creating message reader (kafka avro consumer) for topic ' + topic)
        super().__init__(topic, dump_to_file)

    def instantiate_consumer(self, prop_dict):
        sr_conf = {'url': 'http://localhost:8081'}
        schema_registry_client = SchemaRegistryClient(sr_conf)
        self.avro_deserializer = AvroDeserializer(schema_registry_client)
        self.consumer = Consumer(prop_dict)

    def get_json_string_and_dict(self, msg):
        deserialized_msg = self.avro_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
        return json.dumps(deserialized_msg), deserialized_msg

class KMessageReaderPlainJson(KMessageReader):

    def __init__(self, topic: str, dump_to_file: str=None):
        logger.info('Creating message reader (kafka plain json consumer) for topic ' + topic)
        super().__init__(topic, dump_to_file)

    def instantiate_consumer(self, prop_dict):
        self.consumer = Consumer(prop_dict)

    def get_json_string_and_dict(self, msg):
        decoded_msg = msg.value().decode('utf-8')
        return decoded_msg, json.loads(decoded_msg)

class KMessageReaderList(list):

    def getReaderOfTopicStartingWith(self, txt: str) -> KMessageReader:
        for consumer in self:
            if consumer.topic.startswith(txt):
                return consumer
        return None


#from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka.avro import AvroConsumer
import time

def get_next_message(seconds):
    consumer = AvroConsumer({
        'bootstrap.servers': 'localhost:9092',
        'schema.registry.url': 'http://localhost:8081',
        'security.protocol': 'PLAINTEXT',
        'group.id': 'smoke_test',
        'auto.offset.reset': 'earliest'
    })
    topic = 'daisy.dev.flow-avro-raw'
    consumer.subscribe([topic])
    msg = consumer.poll(seconds)
    consumer.close()
    if msg is None:
        print('No messages read by kafka consumer in ' + str(seconds) + ' seconds - ', end='')
        return False
    if msg.error():
        print("Kafka consumer error: " + str(msg.error()))
        return False
    print('Received following data from pmacct through Kafka: ' + str(msg.value()))
    print('Received ' + str(msg.value()["packets"]) + ' IPFIX packets')
    num_packets = msg.value()["packets"]
    return num_packets>0

#    except SerializerError as e:
#        print("Message deserialization failed for {}: {}".format(msg, e))
#        return False

def check_kafka_packets():
    tries = 20
    ret = get_next_message(5)
    while ret==False:
        tries -= 1
        if tries<1:
            print('Kafka consumer timed out')
            return False
        print('Retrying... ')
        time.sleep(10)
        ret = get_next_message(5)
    print('SUCCESS')
    return True
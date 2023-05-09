
from py_test_tools.helpers import log_message, find_kafka_topic_name, get_current_time_in_milliseconds
import py_test_tools.kafka_consumer as kafka_consumer
import py_test_tools.scripts as scripts
import os, logging
logger = logging.getLogger(__name__)



pmacct_conf_file_fullpath = os.path.dirname(__file__) + '/pmacctd_001.conf'

pmacct_mount_folder_fullpath = os.path.dirname(__file__) + '/pmacct_mount'

kafka_topic_name = find_kafka_topic_name(pmacct_conf_file_fullpath)
print('Kafka topic name: ' + kafka_topic_name)

messages = kafka_consumer.get_all_messages(kafka_topic_name, 5, 1000000)

if not messages or len(messages)<1:
    print('No messages read')
else:
    for msg in messages:
        print(msg.value())



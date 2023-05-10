
from py_test_tools.helpers import log_message, find_kafka_topic_name, get_current_time_in_milliseconds
import py_test_tools.kafka_consumer as kafka_consumer
import py_test_tools.scripts as scripts
import logging
from tests.common.setup_teardown import kafka_infra_setup_teardown, pmacct_setup_teardown
logger = logging.getLogger(__name__)


def test_smoketest(kafka_infra_setup_teardown, pmacct_setup_teardown):
    _,_,_,kafka_topic_name = pmacct_setup_teardown
    time_traffic_started = get_current_time_in_milliseconds()
    packets_sent = scripts.send_ipfix_packets(5)
    time_traffic_stopped = get_current_time_in_milliseconds()
    assert packets_sent>=0
    packet_info = kafka_consumer.check_packets_in_kafka_message(kafka_topic_name, packets_sent)
    assert packet_info!=None
    assert packet_info[0]>=0 # verify that pmacct processed and reported at least 1 packet
    logger.info('Zero offset set as the time when traffic generation started')
    logger.info('Traffic generation finished at ' + str(time_traffic_stopped-time_traffic_started) + 'ms offset')
    logger.info('Pmacct sent first message at ' + str(packet_info[1]-time_traffic_started) + 'ms offset')
    assert packets_sent==packet_info[0]


def test_failingtest(pmacct_setup_teardown):
    _,_,_,kafka_topic_name = pmacct_setup_teardown
    time_traffic_started = get_current_time_in_milliseconds()
    packets_sent = scripts.send_ipfix_packets(5)
    time_traffic_stopped = get_current_time_in_milliseconds()
    assert packets_sent >= 0
    # waiting for only 1 second below guarantees failure, cause no message is read from Kafka within that time
    packet_info = kafka_consumer.check_packets_in_kafka_message(kafka_topic_name, packets_sent, 1)
    assert packet_info != None
    assert packet_info[0] >= 0  # verify that pmacct processed and reported at least 1 packet
    logger.info('Zero offset set as the time when traffic generation started')
    logger.info('Traffic generation finished at ' + str(time_traffic_stopped - time_traffic_started) + 'ms offset')
    logger.info('Pmacct sent first message at ' + str(packet_info[1] - time_traffic_started) + 'ms offset')
    assert packets_sent == packet_info[0]


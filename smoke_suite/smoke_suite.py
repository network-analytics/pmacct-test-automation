
from py_test_tools.helpers import log_message, find_kafka_topic_name, get_current_time_in_milliseconds
import py_test_tools.kafka_consumer as kafka_consumer
import py_test_tools.scripts as scripts
import os, logging
logger = logging.getLogger(__name__)


@log_message('Starting Kafka containers (zoekeeper, broker, schema-registry)')
def setup_module():
    assert not scripts.check_broker_running()
    assert scripts.start_kafka_containers()
    assert scripts.wait_schemaregistry_healthy(120)


class Test_Smoke:

    kafka_topic_name = None

    @log_message('Creating daisy topic and starting pmacct container')
    def setup_class():
        pmacct_conf_file_fullpath = os.path.dirname(__file__) + '/pmacctd.conf'
        assert os.path.isfile(pmacct_conf_file_fullpath)
        pmacct_mount_folder_fullpath = os.path.dirname(__file__) + '/pmacct_mount'
        assert os.path.exists(pmacct_mount_folder_fullpath + '/pmacct_output')
        Test_Smoke.kafka_topic_name = find_kafka_topic_name(pmacct_conf_file_fullpath)
        assert Test_Smoke.kafka_topic_name!=None
        assert scripts.create_or_clear_kafka_topic(Test_Smoke.kafka_topic_name)
        assert scripts.start_pmacct_container(pmacct_conf_file_fullpath, pmacct_mount_folder_fullpath)
        assert scripts.wait_pmacct_running(5) # wait 5 seconds

    @log_message('Smoke test method setup (dummy)')
    def setup_method(self, method):
        pass

    @log_message('Running smoke test functionality')
    def test_smoketest(self):
        time_traffic_started = get_current_time_in_milliseconds()
        packets_sent = scripts.send_smoketest_ipfix_packets()
        time_traffic_stopped = get_current_time_in_milliseconds()
        assert packets_sent>=0
        packet_info = kafka_consumer.check_packets_in_kafka_message(Test_Smoke.kafka_topic_name, packets_sent)
        assert packet_info!=None
        assert packet_info[0]>=0 # verify that pmacct processed and reported at least 1 packet
        logger.info('Zero offset set as the time when traffic generation started')
        logger.info('Traffic generation finished at ' + str(time_traffic_stopped-time_traffic_started) + 'ms offset')
        logger.info('Pmacct sent first message at ' + str(packet_info[1]-time_traffic_started) + 'ms offset')
        assert packets_sent==packet_info[0]

    @log_message('Running failing smoke test functionality')
    def test_failingtest(self):
        time_traffic_started = get_current_time_in_milliseconds()
        packets_sent = scripts.send_smoketest_ipfix_packets()
        time_traffic_stopped = get_current_time_in_milliseconds()
        assert packets_sent >= 0
        # waiting for only 1 second below guarantees failure, cause no message is read from Kafka within that time
        packet_info = kafka_consumer.check_packets_in_kafka_message(Test_Smoke.kafka_topic_name, packets_sent, 1)
        assert packet_info != None
        assert packet_info[0] >= 0  # verify that pmacct processed and reported at least 1 packet
        logger.info('Zero offset set as the time when traffic generation started')
        logger.info('Traffic generation finished at ' + str(time_traffic_stopped - time_traffic_started) + 'ms offset')
        logger.info('Pmacct sent first message at ' + str(packet_info[1] - time_traffic_started) + 'ms offset')
        assert packets_sent == packet_info[0]

    @log_message('Smoke test method teardown (dummy)')
    def teardown_method(self, method):
        pass

    @log_message('Stopping and removing pmacct container')
    def teardown_class():
        scripts.stop_and_remove_pmacct_container()


@log_message('Stopping and removing Kafka containers (zoekeeper, broker, schema-registry)')
def teardown_module():
    scripts.stop_and_remove_kafka_containers()

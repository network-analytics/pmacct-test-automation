
from py_test_tools.helpers import log_message, find_kafka_topic_name
import py_test_tools.kafka_consumer as kafka_consumer
import py_test_tools.scripts as scripts
import os, logging
logger = logging.getLogger(__name__)


@log_message('Starting Kafka containers (zoekeeper, broker, schema-registry)')
def setup_module():
    assert not scripts.check_broker_running()
    assert scripts.start_kafka_containers()
    assert scripts.wait_schemaregistry_healthy(120)


class Test_Signal:

    kafka_topic_name = None
    pmacct_mount_folder_fullpath = None
    pmacct_mount_output_folder = None

    @log_message('Creating daisy topic and starting pmacct container')
    def setup_class():
        pmacct_conf_file_fullpath = os.path.dirname(__file__) + '/pmacctd.conf'
        assert os.path.isfile(pmacct_conf_file_fullpath)
        Test_Signal.pmacct_mount_folder_fullpath = os.path.dirname(__file__) + '/pmacct_mount'
        assert os.path.exists(Test_Signal.pmacct_mount_folder_fullpath)
        Test_Signal.pmacct_mount_output_folder = Test_Signal.pmacct_mount_folder_fullpath + '/pmacct_output'
        assert os.path.exists(Test_Signal.pmacct_mount_output_folder)
        Test_Signal.kafka_topic_name = find_kafka_topic_name(pmacct_conf_file_fullpath)
        assert Test_Signal.kafka_topic_name!=None
        assert scripts.create_or_clear_kafka_topic(Test_Signal.kafka_topic_name)

        with open(Test_Signal.pmacct_mount_folder_fullpath + '/pretag.map', 'w') as f:
            f.write('set_label=nkey%unknown%pkey%unknown')
        assert scripts.start_pmacct_container(pmacct_conf_file_fullpath, Test_Signal.pmacct_mount_folder_fullpath)
        assert scripts.wait_pmacct_running(5) # wait 5 seconds

    @log_message('Signal test method setup (dummy)')
    def setup_method(self, method):
        pass

    @log_message('Running Signal test functionality')
    def test_signaltest(self):
        packets_sent = scripts.send_ipfix_packets()
        assert packets_sent>=0
        packet_info = kafka_consumer.check_packets_and_get_IP(Test_Signal.kafka_topic_name, packets_sent)
        assert packet_info!=None
        assert packet_info[0]>=0 # verify that pmacct processed and reported at least 1 packet
        assert packets_sent==packet_info[0]
        peer_ip = packet_info[1]

        with open(Test_Signal.pmacct_mount_folder_fullpath + '/pretag.map', 'w') as f:
            f.write("set_label=nkey%node_test%pkey%platform_test ip="+peer_ip+"/32\nset_label=nkey%unknown%pkey%unknown")
        assert scripts.send_signal_to_pmacct('SIGUSR2')
        packets_sent = scripts.send_ipfix_packets()
        assert packets_sent >= 0
        packet_info = kafka_consumer.check_packets_in_kafka_message(Test_Signal.kafka_topic_name, packets_sent)
        assert packet_info != None
        assert packet_info[0] >= 0  # verify that pmacct processed and reported at least 1 packet
        assert packets_sent == packet_info[0]

        assert scripts.check_file_for_text(Test_Signal.pmacct_mount_output_folder + "/nfacctd.log", "destroy")


    @log_message('Signal test method teardown (dummy)')
    def teardown_method(self, method):
        pass

    @log_message('Stopping and removing pmacct container')
    def teardown_class():
        scripts.stop_and_remove_pmacct_container()


@log_message('Stopping and removing Kafka containers (zoekeeper, broker, schema-registry)')
def teardown_module():
    scripts.stop_and_remove_kafka_containers()

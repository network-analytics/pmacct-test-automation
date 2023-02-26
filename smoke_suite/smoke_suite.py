
from py_test_tools.helpers import print_message, find_kafka_topic_name
import py_test_tools.kafka_consumer as kafka_consumer
import py_test_tools.scripts as scripts
import os

pmacct_conf_file_fullpath = os.path.dirname(__file__) + '/pmacctd.conf'
kafka_topic_name = find_kafka_topic_name(pmacct_conf_file_fullpath)

@print_message('Starting Kafka containers (zoekeeper, broker, schema-registry)')
def setup_module():
    assert kafka_topic_name!=None
    assert scripts.start_kafka_containers()
    assert scripts.wait_schemaregistry_healthy(120)


class Test_Smoke:

    @print_message('Creating daisy topic and starting pmacct container')
    def setup_class():
        assert scripts.create_daisy_topic(kafka_topic_name)
        assert scripts.start_pmacct_container(pmacct_conf_file_fullpath)
        assert scripts.wait_pmacct_running(5) # wait 5 seconds

    @print_message('Running smoke test functionality')
    def test_smoketest(self):
        packets_sent = scripts.send_smoketest_ipfix_packets()
        assert packets_sent>=0
        packets_processed = kafka_consumer.check_kafka_packets(kafka_topic_name)
        assert packets_processed>=0
        assert packets_sent==packets_processed

    @print_message('Stopping and removing pmacct container')
    def teardown_class():
        scripts.stop_and_remove_pmacct_container()


@print_message('Stopping and removing Kafka containers (zoekeeper, broker, schema-registry)')
def teardown_module():
    scripts.stop_and_remove_kafka_containers()








    # @print_message('Flush and reset Kafka topic')
    # def setup_method(self, method):
    #     # run before each test case starts
    #     pass

    # @print_message('Make sure traffic generator has finished')
    # def teardown_method(self, method):
    #     # run after each test case finishes
    #     pass

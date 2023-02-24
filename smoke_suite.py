import kafka_consumer
import run_scripts as scripts
from helpers import print_message


@print_message('Starting Kafka containers (zoekeeper, broker, schema-registry)')
def setup_module():
    assert scripts.start_kafka_containers()
    assert scripts.wait_schemaregistry_healthy(120)


class Test_Smoke:

    #pmacct_conf_file = 'nfacctd-ipfix-basic.conf'
    #kafka_topic_name = 'smoke_kafka_topic'

    @print_message('Creating daisy topic and starting pmacct container')
    def setup_class():
        assert scripts.create_daisy_topic()
        assert scripts.start_pmacct_container()
        assert scripts.wait_pmacct_running(5) # wait 5 seconds

    @print_message('Running smoke test functionality')
    def test_smoketest(self):
        assert scripts.send_ipfix_packets()
        assert kafka_consumer.check_kafka_packets()

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


from py_test_tools.helpers import log_message, find_kafka_topic_name, get_current_time_in_milliseconds
import py_test_tools.kafka_consumer as kafka_consumer
import py_test_tools.scripts as scripts
import os, logging
logger = logging.getLogger(__name__)


@log_message('Starting Kafka containers (zoekeeper, broker, schema-registry)')
def setup_module():
    if scripts.check_broker_running():
        return
    assert scripts.start_kafka_containers()
    assert scripts.wait_schemaregistry_healthy(120)


class Test_001:

    kafka_topic_name = None

    @log_message('Creating daisy topic and starting pmacct container')
    def setup_class():
        pmacct_conf_file_fullpath = os.path.dirname(__file__) + '/pmacctd_001.conf'
        assert os.path.isfile(pmacct_conf_file_fullpath)

        Test_001.pcap_config_file = os.path.dirname(__file__) + '/traffic-reproducer-00.conf'
        assert os.path.isfile(Test_001.pcap_config_file)
        #        scripts.replace_in_file(Test_001.pcap_config_file, '<path_to>', os.path.dirname(__file__))

        Test_001.pmacct_mount_folder_fullpath = os.path.dirname(__file__) + '/pmacct_mount'
        assert os.path.exists(Test_001.pmacct_mount_folder_fullpath)
        Test_001.pmacct_mount_output_folder = Test_001.pmacct_mount_folder_fullpath + '/pmacct_output'
        assert os.path.exists(Test_001.pmacct_mount_output_folder)
        Test_001.kafka_topic_name = find_kafka_topic_name(pmacct_conf_file_fullpath)
        assert Test_001.kafka_topic_name != None
        assert scripts.create_or_clear_kafka_topic(Test_001.kafka_topic_name)

        with open(Test_001.pmacct_mount_folder_fullpath + '/pretag.map', 'w') as f:
            f.write('set_label=nkey%unknown%pkey%unknown')
        assert scripts.start_pmacct_container(pmacct_conf_file_fullpath, Test_001.pmacct_mount_folder_fullpath)
        assert scripts.wait_pmacct_running(5)  # wait 5 seconds

    @log_message('Running smoke test functionality')
    def test_smoketest(self):
        pass






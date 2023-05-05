
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
        pass

    @log_message('Smoke test method teardown (dummy)')
    def teardown_method(self, method):
        pass





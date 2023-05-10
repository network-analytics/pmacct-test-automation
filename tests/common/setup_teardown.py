
import py_test_tools.scripts as scripts
import logging, pytest, os
from py_test_tools.helpers import find_kafka_topic_name
logger = logging.getLogger(__name__)


#@log_message('Starting Kafka containers (zoekeeper, broker, schema-registry)')
@pytest.fixture(scope="session")
def kafka_infra_setup_teardown():
    assert not scripts.check_broker_running()
    assert scripts.start_kafka_containers()
    assert scripts.wait_schemaregistry_healthy(120)
    yield
    scripts.stop_and_remove_kafka_containers()


@pytest.fixture(scope="module")
def pmacct_setup_teardown(request):
    pmacct_conf_file_fullpath = os.path.dirname(request.module.__file__) + '/pmacctd.conf'
    assert os.path.isfile(pmacct_conf_file_fullpath)
    pmacct_mount_folder_fullpath = os.path.dirname(request.module.__file__) + '/pmacct_mount'
    assert os.path.exists(pmacct_mount_folder_fullpath)
    pmacct_mount_output_folder = pmacct_mount_folder_fullpath + '/pmacct_output'
    assert os.path.exists(pmacct_mount_output_folder)
    kafka_topic_name = find_kafka_topic_name(pmacct_conf_file_fullpath)
    assert kafka_topic_name!=None
    assert scripts.create_or_clear_kafka_topic(kafka_topic_name)
    assert scripts.start_pmacct_container(pmacct_conf_file_fullpath, pmacct_mount_folder_fullpath)
    assert scripts.wait_pmacct_running(5) # wait 5 seconds
    yield pmacct_conf_file_fullpath, pmacct_mount_folder_fullpath, pmacct_mount_output_folder, kafka_topic_name
    scripts.stop_and_remove_pmacct_container()

    # TODO also delete nfacctd.log in the setup, so that logs only reflect latest run

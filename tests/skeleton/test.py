
from library.py.configuration_file import KConfigurationFile
from library.py.setup_tools import KModuleParams
from library.py.kafka_consumer import KMessageReader
import library.py.scripts as scripts
import os, logging, pytest, sys
logger = logging.getLogger(__name__)

testModuleParams = KModuleParams(sys.modules[__name__])
confFile = KConfigurationFile(testModuleParams.test_conf_file)

@pytest.fixture(scope="session")
def kafka_infra_setup():
    assert not scripts.check_broker_running()
    assert scripts.start_kafka_containers()
    assert scripts.wait_schemaregistry_healthy(120)

@pytest.fixture(scope="session")
def kafka_infra_teardown():
    yield
    scripts.stop_and_remove_kafka_containers()

@pytest.fixture(scope="module")
def pmacct_setup(request):
    params = request.module.testModuleParams
    assert os.path.isfile(params.results_conf_file)
    assert params.kafka_topic_name != None
    assert scripts.create_or_clear_kafka_topic(params.kafka_topic_name)
    assert scripts.start_pmacct_container(params.results_conf_file, params.results_mount_folder)
    assert scripts.wait_pmacct_running(5)  # wait 5 seconds

@pytest.fixture(scope="module")
def pmacct_teardown(request):
    yield
    scripts.stop_and_remove_pmacct_container()

def test_start_kafka(check_root_dir, kafka_infra_setup):
    assert True

def test_start_pmacct(check_root_dir, prepare_test, pmacct_setup):
    assert True

def test_stop_kafka(kafka_infra_teardown):
    assert True

def test_stop_pmacct(pmacct_teardown):
    assert True

def test_read_messages():
    consumer = KMessageReader(testModuleParams.kafka_topic_name, testModuleParams.results_msg_dump)
    messages = consumer.get_all_messages(5, 1)
    if not messages or len(messages) < 1:
        print('No messages read')
    else:
        for msg in messages:
            print(msg.value())

def test_prepare(prepare_test):
    logger.info(vars(testModuleParams))
    assert True

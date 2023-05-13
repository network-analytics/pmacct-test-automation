
import library.py.kafka_consumer as kafka_consumer
import library.py.scripts as scripts
import os, logging, pytest, sys
from library.fixtures.prepare import check_root_dir, prepare_test, KModuleParams
from library.fixtures.setup_teardown import kafka_infra_setup_teardown, pmacct_setup_teardown
logger = logging.getLogger(__name__)

testModuleParams = KModuleParams(sys.modules[__name__])

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
    messages = kafka_consumer.get_all_messages(testModuleParams.kafka_topic_name, 5, 1)
    if not messages or len(messages) < 1:
        print('No messages read')
    else:
        for msg in messages:
            print(msg.value())


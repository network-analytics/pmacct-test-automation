
import library.py.scripts as scripts
import logging, pytest, os, shutil
from library.py.helpers import find_kafka_topic_name
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def kafka_infra_setup_teardown():
    assert not scripts.check_broker_running()
    assert scripts.start_kafka_containers()
    assert scripts.wait_schemaregistry_healthy(120)
    yield
    scripts.stop_and_remove_kafka_containers()


@pytest.fixture(scope="module")
def pmacct_setup_teardown(request):
    params = request.module.testModuleParams
    assert os.path.isfile(params.results_conf_file)
    assert params.kafka_topic_name != None
    assert scripts.create_or_clear_kafka_topic(params.kafka_topic_name)
    assert scripts.start_pmacct_container(params.results_conf_file, params.results_mount_folder)
    assert scripts.wait_pmacct_running(5)  # wait 5 seconds
    yield
    scripts.stop_and_remove_pmacct_container()


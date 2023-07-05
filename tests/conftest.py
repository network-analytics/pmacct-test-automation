
import library.py.scripts as scripts
import library.py.setup_tools as setup_tools
import logging, pytest, os
from library.py.kafka_consumer import KMessageReader
logger = logging.getLogger(__name__)


def setup_kafka_infra():
    assert not scripts.check_broker_running()
    assert scripts.create_test_network()
    assert scripts.start_kafka_containers()
    assert scripts.wait_schemaregistry_healthy(120)


@pytest.fixture(scope="session")
def kafka_infra_setup_teardown():
    setup_kafka_infra()
    yield
    scripts.stop_and_remove_kafka_containers()
    scripts.delete_test_network()


# For troubleshooting/debugging only!
@pytest.fixture(scope="session")
def kafka_infra_setup():
    setup_kafka_infra()


def setup_pmacct(request):
    params = request.module.testParams
    assert os.path.isfile(params.results_conf_file)
    assert params.kafka_topic_name != None
    #    assert scripts.delete_registered_schemas()
    for topic in list(params.kafka_topics.values()):
        assert scripts.create_or_clear_kafka_topic(topic)
    # assert scripts.create_or_clear_kafka_topic(params.kafka_topic_name)
    assert scripts.start_pmacct_container(params.results_conf_file, params.results_mount_folder) #, params.pmacct_ip)
    assert scripts.wait_pmacct_running(5)  # wait 5 seconds


@pytest.fixture(scope="module")
def pmacct_setup_teardown(request):
    setup_pmacct(request)
    yield
    scripts.stop_and_remove_all_traffic_containers()
    scripts.stop_and_remove_pmacct_container()


# For troubleshooting/debugging only!
@pytest.fixture(scope="module")
def pmacct_setup(request):
    setup_pmacct(request)


# Makes sure the framework is run from the right directory
@pytest.fixture(scope="session")
def check_root_dir():
    logger.debug('Framework runs from directory: ' + os.getcwd())
    assert os.path.basename(os.getcwd())=='net_ana'


def setup_consumer(request, plainJson):
    params = request.module.testParams
    consumers = []
    for k in params.kafka_topics.keys():
        consumer = KMessageReader(params.kafka_topics[k], params.results_msg_dump, plainJson)
        consumer.connect()
        consumers.append(consumer)
    return consumers

@pytest.fixture(scope="module")
def consumer_setup_teardown(request):
    consumers = setup_consumer(request, False)
    logger.debug('Local setup Consumer ' + str(consumers))
    yield consumers
    logger.debug('Local teardown Consumer ' + str(consumers))
    for consumer in consumers:
        consumer.disconnect()


@pytest.fixture(scope="module")
def consumerJson_setup_teardown(request):
    consumers = setup_consumer(request, True)
    logger.debug('Local setup Consumer ' + str(consumers))
    yield consumers
    logger.debug('Local teardown Consumer ' + str(consumers))
    for consumer in consumers:
        consumer.disconnect()

# Prepares results folder to receive logs and output from pmacct
@pytest.fixture(scope="module")
def prepare_test(request):
    setup_tools.prepare_test_env(request.module)

# Prepares
@pytest.fixture(scope="module")
def prepare_pcap(request):
    setup_tools.prepare_pcap(request.module)


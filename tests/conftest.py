###################################################
# Automated Testing Framework for Network Analytics
# Central fixtures definition; used by all tests
# nikolaos.tsokas@swisscom.com 11/05/2023
###################################################

import library.py.scripts as scripts
import library.py.setup_tools as setup_tools
import logging, pytest, os
import library.py.helpers as helpers
from library.py.kafka_consumer import KMessageReaderAvro, KMessageReaderPlainJson, KMessageReaderList
logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption("--scenario", action="store", default="default")


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


# Setup only - for troubleshooting/debugging only!
@pytest.fixture(scope="session")
def kafka_infra_setup():
    setup_kafka_infra()


@pytest.fixture(scope="module")
def pmacct_logcheck(request):
    params = request.module.testParams
    def checkfunction():
        return os.path.isfile(params.pmacct_log_file) and \
            helpers.check_regex_sequence_in_file(params.pmacct_log_file,
                ['_core/core .+ waiting for .+ data on interface'])
    assert helpers.retry_until_true('Pmacct first log line', checkfunction, 30, 5)
    params.pmacct_version = helpers.read_pmacct_version(params.pmacct_log_file)
    assert params.pmacct_version
    logger.info('Pmacct version: ' + params.pmacct_version)


def setup_pmacct(request):
    params = request.module.testParams
    assert os.path.isfile(params.results_conf_file)
    for topic in list(params.kafka_topics.values()):
        assert scripts.create_or_clear_kafka_topic(topic)
    img_var_name = 'PMACCT_' + params.daemon.upper() + '_IMG'
    config = helpers.read_config_file(params.root_folder + '/settings.conf')
    pmacct_img = config.get(img_var_name)
    assert scripts.start_pmacct_container(params.results_conf_file, params.results_mount_folder, params.daemon,
        pmacct_img)
    assert scripts.wait_pmacct_running(5)  # wait 5 seconds


@pytest.fixture(scope="module")
def pmacct_setup_teardown(request):
    setup_pmacct(request)
    yield
    scripts.stop_and_remove_all_traffic_containers()
    rsc_msg = ['Pmacct container resources:']
    rsc_msg += [' '+x for x in helpers.container_resources_string(scripts.get_pmacct_stats())]
    for msg in rsc_msg:
        logger.info(msg)
    scripts.stop_and_remove_pmacct_container()


@pytest.fixture(scope="module")
def redis_setup_teardown(request):
    assert scripts.start_redis_container()
    assert scripts.wait_redis_running(5)  # wait up to 5 seconds
    yield
    scripts.stop_and_remove_redis_container()


# Setup only - for troubleshooting/debugging only!
@pytest.fixture(scope="module")
def pmacct_setup(request):
    setup_pmacct(request)


# Fixture makes sure the framework is run from the right directory
@pytest.fixture(scope="session")
def check_root_dir():
    logger.debug('Framework runs from directory: ' + os.getcwd())
    assert all(x in os.listdir(os.getcwd()) for x in ['tools', 'tests', 'library', 'pytest.ini', 'settings.conf'])
    assert os.path.dirname(__file__) == os.getcwd() + '/tests'



def setup_consumers(request):
    params = request.module.testParams
    consumers = KMessageReaderList()
    for k in params.kafka_topics.keys():
        topic_name = '_'.join(params.kafka_topics[k].split('.')[0:-1])
        messageReaderClass = KMessageReaderAvro
        if topic_name.endswith('_json'):
            messageReaderClass = KMessageReaderPlainJson
        msg_dump_file = params.results_folder + '/' + topic_name + '_dump.json'
        consumer = messageReaderClass(params.kafka_topics[k], msg_dump_file)
        consumer.connect()
        consumers.append(consumer)
    logger.debug('Local setup Consumers ' + str(consumers))
    return consumers


def teardown_consumers(consumers):
    logger.debug('Local teardown Consumers ' + str(consumers))
    for consumer in consumers:
        consumer.disconnect()


@pytest.fixture(scope="module")
def consumer_setup_teardown(request):
    consumers = setup_consumers(request) # , KMessageReaderAvro)
    yield consumers
    teardown_consumers(consumers)


# Prepares results folder to receive logs and output from pmacct
@pytest.fixture(scope="module")
def prepare_test(request):
    scenario = request.config.getoption('--scenario')
    logger.info('Scenario selected: ' + scenario)
    setup_tools.prepare_test_env(request.module, scenario)


# Prepares folders with pcap information for traffic-reproduction containers to mount
@pytest.fixture(scope="module")
def prepare_pcap(request):
    setup_tools.prepare_pcap(request.module)


# No teardown - only for debugging
@pytest.fixture(scope="module")
def debug_core(check_root_dir, prepare_test, pmacct_setup, prepare_pcap):
    pass


# Adds a banner with the test case name to the logs at the start and the end of the execution
@pytest.fixture(scope="module")
def test_name_logging(request):
    params = request.module.testParams
    def logMessage(msg):
        txts = ['*'*len(msg), '*'*len(msg), msg, '*'*len(msg), '*'*len(msg)]
        for txt in txts:
            logger.info(txt)
    logMessage('** Starting test: ' + params.test_name + ' **')
    yield
    logMessage('** Finishing test: ' + params.test_name + ' **')


# Abstract fixture, which incorporates all common (core) fixtures
@pytest.fixture(scope="module")
def test_core(check_root_dir, kafka_infra_setup_teardown, test_name_logging, prepare_test, pmacct_setup_teardown,
              pmacct_logcheck, prepare_pcap):
    pass

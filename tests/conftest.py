###################################################
# Automated Testing Framework for Network Analytics
# Central fixtures definition; used by all tests
# nikolaos.tsokas@swisscom.com 11/05/2023
###################################################

import library.py.scripts as scripts
import library.py.setup_tools as setup_tools
import logging, pytest, os, re
import library.py.helpers as helpers
from library.py.kafka_consumer import KMessageReaderAvro, KMessageReaderPlainJson, KMessageReaderList
logger = logging.getLogger(__name__)


# Defines parameter for receiving configuration in the form <test case>:<scenario>
def pytest_addoption(parser):
    parser.addoption("--runconfig", action="store", default="")


# Runs for every test case collected by pytest from the files. By parameterizing the top test -level fixture,
# clones the test case for every possible scenario, i.e., for every scenario, for which a subfolder exists
def pytest_generate_tests(metafunc):
    scen_folders = helpers.select_files(metafunc.module.testParams.test_folder, 'scenario-\\d{2}$')
    scenarios = ['default'] + [os.path.basename(s) for s in scen_folders if os.path.isdir(s)]
    logger.debug('Test ' + os.path.basename(os.path.dirname(metafunc.module.__file__)) +
                ' is cloned for following scenarios: ' + str(scenarios))
    metafunc.parametrize('test_name_logging', scenarios, scope='function')


# Runs at the end of the pytest collection process. Restricts test case execution to the selected
# scenarios (not selected scenarios are skipped)
def pytest_collection_modifyitems(config, items):
    runconfig = config.getoption('runconfig').replace('*', '').split('_')
    config_tuples = []
    for rc in runconfig:
        rclist = rc.split(':')
        test_prefix = rclist[0]
        selected_scenario = '<all scenarios>'
        if len(rclist)>1 and rclist[1]!='':
            selected_scenario = 'scenario-' + rclist[1] if rclist[1] != '00' else 'default'
        config_tuples.append((test_prefix, selected_scenario))
    logger.info('Selected scenario per test case:' + str(config_tuples))
    skip = pytest.mark.skip(reason="Scenario not selected - skipped")
    count_skipped = 0
    for item in items:
        for tpl in config_tuples:
            if os.path.basename(item.module.testParams.test_folder).startswith(tpl[0]):
                if tpl[1]!='<all scenarios>' and not item.name.endswith('['+tpl[1]+']'):
                    logger.debug('Skipping ' + os.path.basename(item.module.testParams.test_folder) + item.name +
                                 ' (scenario not selected)')
                    count_skipped += 1
                    item.add_marker(skip)
    if count_skipped>0:
        logger.info('Skipping ' + str(count_skipped) + ' of ' + str(len(items)) + ' collected items')


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


@pytest.fixture(scope="function")
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


def setup_pmacct(params):
    assert os.path.isfile(params.results_conf_file)
    for topic in list(params.kafka_topics.values()):
        assert scripts.create_or_clear_kafka_topic(topic)
    params.create_pmacct_compose_file()
    assert scripts.start_pmacct_container(params.pmacct_docker_compose_file)
    assert scripts.wait_pmacct_running(5)  # wait 5 seconds


@pytest.fixture(scope="function")
def pmacct_setup_teardown(prepare_test, request):
    params = request.module.testParams
    scenario = prepare_test
    setup_pmacct(params)
    yield scenario
    scripts.stop_and_remove_all_traffic_containers()
    rsc_msg = ['Pmacct container resources:']
    rsc_msg += [' '+x for x in helpers.container_resources_string(scripts.get_pmacct_stats())]
    for msg in rsc_msg:
        logger.info(msg)
    scripts.stop_and_remove_pmacct_container(params.pmacct_docker_compose_file)


@pytest.fixture(scope="function")
def redis_setup_teardown(request):
    assert scripts.start_redis_container()
    assert scripts.wait_redis_running(5)  # wait up to 5 seconds
    yield
    scripts.stop_and_remove_redis_container()


# Setup only - for troubleshooting/debugging only!
@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
def consumer_setup_teardown(request):
    consumers = setup_consumers(request) # , KMessageReaderAvro)
    yield consumers
    teardown_consumers(consumers)


# Prepares results folder to receive logs and output from pmacct
@pytest.fixture(scope="function")
def prepare_test(test_name_logging, request):
    scenario = test_name_logging
    logger.info('Scenario selected: ' + scenario)
    setup_tools.prepare_test_env(request.module, scenario)
    yield scenario


# Prepares folders with pcap information for traffic-reproduction containers to mount
@pytest.fixture(scope="function")
def prepare_pcap(request):
    setup_tools.prepare_pcap(request.module)


# No teardown - only for debugging
@pytest.fixture(scope="function")
def debug_core(check_root_dir, prepare_test, pmacct_setup, prepare_pcap):
    pass

# This is the top level of function-scoped fixture, therefore it gets the scenario param
# Adds a banner with the test case name to the logs at the start and the end of the execution
@pytest.fixture(scope="function")
def test_name_logging(request):
    scenario = request.param
    params = request.module.testParams
    def logMessage(msg):
        txts = ['*'*len(msg), '*'*len(msg), msg, '*'*len(msg), '*'*len(msg)]
        for txt in txts:
            logger.info(txt)
    logMessage('** Starting test: ' + params.test_name + ' **\n** Scenario:      ' + scenario + '     **\n' )
    # Since this is module-level scope setup, pmacct is not yet running, therefore no concurrency
    # issues with monitor.sh are expected, even though logging to the same file
    with open(request.module.testParams.monitor_file, 'a') as f:
        f.write('** Starting test: ' + params.test_name + ' **\n')
    yield scenario
    logMessage('** Finishing test: ' + params.test_name + ' **\n')


# Abstract fixture, which incorporates all common (core) fixtures
@pytest.fixture(scope="function")
def test_core(check_root_dir, kafka_infra_setup_teardown, pmacct_setup_teardown, pmacct_logcheck, prepare_pcap):
    pass


from library.py.configuration_file import KConfigurationFile
from library.py.setup_tools import KModuleParams
#import library.py.kafka_consumer as kafka_consumer
from library.py.kafka_consumer import KMessageReader
import library.py.scripts as scripts
import library.py.json_tools as jsontools
import library.py.helpers as helpers
import os, logging, pytest, sys, shutil, json
logger = logging.getLogger(__name__)

# The below two variables are used by setup_tools.prepare_test_env
testModuleParams = KModuleParams(sys.modules[__name__])
confFile = KConfigurationFile(testModuleParams.test_conf_file)

@pytest.fixture
def prepare_pcap():
    test_config_file = testModuleParams.test_folder + '/traffic-reproducer-00.conf'
    test_pcap_file = testModuleParams.test_folder + '/traffic-00.pcap'
    test_output_file = testModuleParams.test_folder + '/output-00.json'
    assert os.path.isfile(test_pcap_file)
    results_config_file = testModuleParams.results_folder + '/traffic-reproducer-00.conf'
    results_pcap_file = testModuleParams.results_folder + '/traffic-00.pcap'
    results_output_file = testModuleParams.results_folder + '/output-00.json'
    shutil.copy(test_config_file, results_config_file)
    shutil.copy(test_pcap_file, results_pcap_file)
    shutil.copy(test_output_file, results_output_file)

    # fix pcap filename absolute path
    with open(results_config_file) as f:
        lines = f.readlines()
    lines[0] = 'pcap: ' + results_pcap_file + '\n'
    with open(results_config_file, "w") as f:
        f.writelines(lines)

    yield (results_config_file, results_output_file)


def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, prepare_pcap, pmacct_setup_teardown):
    consumer = KMessageReader(testModuleParams.kafka_topic_name, testModuleParams.results_msg_dump)
    pcap_config_file, output_file = prepare_pcap
    assert os.path.isfile(pcap_config_file)
    scripts.replay_pcap_file(pcap_config_file)
    messages = consumer.get_messages(120, 12)

    logger.info('Checking for ERROR or WARN')
    assert not helpers.check_regex_sequence_in_file(testModuleParams.results_log_file, ['(ERROR|WARN)'])

    assert len(messages) > 0
    with open(output_file) as f:
        lines = f.readlines()
    jsons = [json.dumps(msg.value()) for msg in messages]
    ignore_fields = ['timestamp_max', 'peer_ip_src', 'timestamp_arrival', 'stamp_inserted', 'timestamp_min', \
                     'stamp_updated']
    assert jsontools.compare_json_lists(jsons, lines, ignore_fields)


from library.py.helpers import log_message, find_kafka_topic_name
import library.py.kafka_consumer as kafka_consumer
import library.py.scripts as scripts
import os, logging, pytest, sys, shutil
from library.fixtures.prepare import check_root_dir, prepare_test, KModuleParams
from library.fixtures.setup_teardown import kafka_infra_setup_teardown, pmacct_setup_teardown
logger = logging.getLogger(__name__)

testModuleParams = KModuleParams(sys.modules[__name__])

@pytest.fixture
def prepare_pcap():
    test_config_file = testModuleParams.test_folder + '/traffic-reproducer-00.conf'
    test_pcap_file = testModuleParams.test_folder + '/traffic-00.pcap'
    assert os.path.isfile(test_pcap_file)
    results_config_file = testModuleParams.results_folder + '/traffic-reproducer-00.conf'
    results_pcap_file = testModuleParams.results_folder + '/traffic-00.pcap'
    shutil.copy(test_config_file, results_config_file)
    shutil.copy(test_pcap_file, results_pcap_file)

    # fix pcap filename absolute path
    with open(results_config_file) as f:
        lines = f.readlines()
    lines[0] = 'pcap: ' + results_pcap_file + '\n'
    with open(results_config_file, "w") as f:
        f.writelines(lines)

    yield results_config_file


def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, prepare_pcap, pmacct_setup_teardown):
    pcap_config_file = prepare_pcap
    assert os.path.isfile(pcap_config_file)
    scripts.replay_pcap_file(pcap_config_file)
    messages = kafka_consumer.get_all_messages(testModuleParams.kafka_topic_name, 120, 12)
    assert len(messages) > 0


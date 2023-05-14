
from library.py.setup_tools import KModuleParams
import library.py.kafka_consumer as kafka_consumer
import library.py.scripts as scripts
import library.py.helpers as helpers
import library.py.json_tools as json_tools
import os, logging, pytest, sys
logger = logging.getLogger(__name__)

testModuleParams = KModuleParams(sys.modules[__name__])


@pytest.fixture(scope="module")
def prepare_pretag(): # run before pmacct is set up
    logger.info('Creating initial pretag.map ' + testModuleParams.results_mount_folder + '/pretag.map')
    with open(testModuleParams.results_mount_folder + '/pretag.map', 'w') as f:
        f.write('set_label=nkey%unknown%pkey%unknown')
    logger.info('Pretag.map created')


def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, prepare_pretag, pmacct_setup_teardown):
    packets_sent = scripts.send_ipfix_packets()
    assert packets_sent>=0
    packet_info = kafka_consumer.check_packets_and_get_IP(testModuleParams.kafka_topic_name, packets_sent)
    assert packet_info!=None
    assert packet_info[0]>=0 # verify that pmacct processed and reported at least 1 packet
    assert packets_sent==packet_info[0]
    peer_ip = packet_info[1]

    with open(testModuleParams.results_mount_folder + '/pretag.map', 'w') as f:
        f.write("set_label=nkey%node_test%pkey%platform_test ip="+peer_ip+"/32\nset_label=nkey%unknown%pkey%unknown")

    assert scripts.send_signal_to_pmacct('SIGUSR2')
    packets_sent = scripts.send_ipfix_packets(5)
    assert packets_sent >= 0
    packet_info = kafka_consumer.check_packets_in_kafka_message(testModuleParams.kafka_topic_name, packets_sent)
    assert packet_info != None
    assert packet_info[0] >= 0  # verify that pmacct processed and reported at least 1 packet
    assert packets_sent == packet_info[0]

    assert helpers.check_regex_sequence_in_file(testModuleParams.results_log_file, \
                                                ['destroying index', 'map successfully \(re\)loaded'])
    logger.info('Right pattern identified in pmacct log')

    assert json_tools.is_part_of_json({"label": {"nkey": "node_test", "pkey": "platform_test"}}, packet_info[2])
    logger.info('Right pattern identified in Kafka message')

    logger.info('Checking for ERROR or WARN')
    assert not helpers.check_regex_sequence_in_file(testModuleParams.results_log_file, ['(ERROR|WARN)'])

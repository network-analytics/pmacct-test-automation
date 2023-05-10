
from py_test_tools.helpers import log_message, find_kafka_topic_name
import py_test_tools.kafka_consumer as kafka_consumer
import py_test_tools.scripts as scripts
import os, logging, pytest
from tests.common.setup_teardown import kafka_infra_setup_teardown, pmacct_setup_teardown
logger = logging.getLogger(__name__)


@pytest.fixture
def prepare_pretag(): # run before pmacct is set up
    pmacct_mount_folder_fullpath = os.path.dirname(__file__) + '/pmacct_mount'
    with open(pmacct_mount_folder_fullpath + '/pretag.map', 'w') as f:
        f.write('set_label=nkey%unknown%pkey%unknown')


def test(kafka_infra_setup_teardown, prepare_pretag, pmacct_setup_teardown):
    pmacct_conf_file_fullpath, pmacct_mount_folder_fullpath, pmacct_mount_output_folder, \
        kafka_topic_name = pmacct_setup_teardown
    packets_sent = scripts.send_ipfix_packets()
    assert packets_sent>=0
    packet_info = kafka_consumer.check_packets_and_get_IP(kafka_topic_name, packets_sent)
    assert packet_info!=None
    assert packet_info[0]>=0 # verify that pmacct processed and reported at least 1 packet
    assert packets_sent==packet_info[0]
    peer_ip = packet_info[1]
    with open(pmacct_mount_folder_fullpath + '/pretag.map', 'w') as f:
        f.write("set_label=nkey%node_test%pkey%platform_test ip="+peer_ip+"/32\nset_label=nkey%unknown%pkey%unknown")
    assert scripts.send_signal_to_pmacct('SIGUSR2')
    packets_sent = scripts.send_ipfix_packets()
    assert packets_sent >= 0
    packet_info = kafka_consumer.check_packets_in_kafka_message(kafka_topic_name, packets_sent)
    assert packet_info != None
    assert packet_info[0] >= 0  # verify that pmacct processed and reported at least 1 packet
    assert packets_sent == packet_info[0]
    assert scripts.check_file_for_text(pmacct_mount_output_folder + "/nfacctd.log", "destroy")


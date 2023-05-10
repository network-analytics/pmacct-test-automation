
from py_test_tools.helpers import log_message, find_kafka_topic_name
import py_test_tools.kafka_consumer as kafka_consumer
import py_test_tools.scripts as scripts
import os, logging, pytest
from tests.common.setup_teardown import kafka_infra_setup_teardown, pmacct_setup_teardown
logger = logging.getLogger(__name__)

# TODO fix absolute path of pcap file in traffic-reproducer.conf

@pytest.fixture
def prepare_pcap():
    pcap_config_file = os.path.dirname(__file__) + '/traffic-reproducer-00.conf'
    assert os.path.isfile(pcap_config_file)
    yield pcap_config_file


def test(kafka_infra_setup_teardown, prepare_pcap, pmacct_setup_teardown):
    _,_,_,kafka_topic_name = pmacct_setup_teardown
    pcap_config_file = prepare_pcap
    scripts.replay_pcap_file(pcap_config_file)
    messages = kafka_consumer.get_all_messages(kafka_topic_name, 120, 12)
    assert len(messages)>0


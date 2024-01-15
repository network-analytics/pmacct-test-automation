
from library.py.setup_tools import KModuleParams
import library.py.helpers as helpers
import library.py.scripts as scripts
import library.py.test_tools as test_tools
import logging, pytest, sys
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], daemon='nfacctd', ipv4_subnet='192.168.100.')

@pytest.mark.nfacctd
@pytest.mark.ipfix
@pytest.mark.ipfix_only
@pytest.mark.ipfixv10
@pytest.mark.avro
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def main(consumer):
    assert scripts.replay_pcap(testParams.pcap_folders[0])

    assert test_tools.read_and_compare_messages(consumer, testParams, 'flow-00',
        ['stamp_inserted', 'stamp_updated', 'timestamp_max', 'timestamp_arrival', 'timestamp_min'])
    
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN'])

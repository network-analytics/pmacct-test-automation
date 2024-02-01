
from library.py.test_params import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], daemon='nfacctd')

@pytest.mark.nfacctd
@pytest.mark.ipfix
@pytest.mark.ipfixv10
@pytest.mark.bmp
@pytest.mark.bmpv3
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown)

def main(consumers):
    # Reproduce all the pcap files
    for i in range(len(testParams.pcap_folders)):
        assert scripts.replay_pcap_detached(testParams.pcap_folders[i])

    assert test_tools.read_and_compare_messages(consumers.getReaderOfTopicStartingWith('daisy.flow'),
        testParams, 'flow-00',
        ['stamp_inserted', 'stamp_updated', 'timestamp_max', 'timestamp_arrival', 'timestamp_min'])

    assert test_tools.read_and_compare_messages(consumers.getReaderOfTopicStartingWith('daisy.bmp'),
        testParams, 'bmp-00',
        ['seq', 'timestamp', 'timestamp_arrival', 'bmp_router_port'])

    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN(?!.*Unable to get kafka_host)'])


from library.py.test_params import KModuleParams
from library.py.test_helper import KTestHelper
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(__file__, daemon='nfacctd')

@pytest.mark.nfacctd
@pytest.mark.ipfix
@pytest.mark.bgp
@pytest.mark.basic
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown)

def main(consumers):
    th = KTestHelper(testParams, consumers)
    assert th.spawn_traffic_container('traffic-reproducer-502', detached=True)

    th.set_ignored_fields(['stamp_inserted', 'stamp_updated', 'timestamp_max', 'timestamp_arrival', 'timestamp_min'])
    assert th.read_and_compare_messages('daisy.flow', 'flow-00')
    th.set_ignored_fields(['seq', 'timestamp', 'timestamp_arrival', 'peer_tcp_port'])
    assert th.read_and_compare_messages('daisy.bgp', 'bgp-00')

    assert not th.check_regex_in_pmacct_log('ERROR|WARN(?!.*Unable to get kafka_host)')


    # assert scripts.replay_pcap_detached(testParams.pcap_folders[0], 0)
    #
    # assert test_tools.read_and_compare_messages(consumers.getReaderOfTopicStartingWith('daisy.flow'),
    #     testParams, 'flow-00',
    #     ['stamp_inserted', 'stamp_updated', 'timestamp_max', 'timestamp_arrival', 'timestamp_min'])
    #
    # assert test_tools.read_and_compare_messages(consumers.getReaderOfTopicStartingWith('daisy.bgp'),
    #     testParams, 'bgp-00',
    #     ['seq', 'timestamp', 'timestamp_arrival', 'peer_tcp_port'])
    #
    # assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN(?!.*Unable to get kafka_host)'])

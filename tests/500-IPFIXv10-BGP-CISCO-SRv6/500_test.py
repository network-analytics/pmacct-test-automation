
from library.py.test_params import KModuleParams
import logging
import pytest
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(__file__, daemon='nfacctd', ipv4_subnet='192.168.100.')


@pytest.mark.nfacctd
@pytest.mark.ipfix
@pytest.mark.bgp
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown)


def main(consumers):
    th = test_tools.KTestHelper(testParams, consumers)
    assert th.spawn_traffic_container('traffic-reproducer-500', detached=True)

    th.set_ignored_fields(['stamp_inserted', 'stamp_updated', 'timestamp_max', 'timestamp_arrival', 'timestamp_min'])
    assert th.read_and_compare_messages('daisy.flow', 'flow-00')
    th.set_ignored_fields(['seq', 'timestamp', 'timestamp_arrival', 'peer_tcp_port'])
    assert th.read_and_compare_messages('daisy.bgp', 'bgp-00')

    th.transform_log_file('log-00', 'traffic-reproducer-500')
    assert th.check_file_regex_sequence_in_pmacct_log('log-00')
    assert not th.check_regex_in_pmacct_log('ERROR|WARN')

    logger.info('Stopping traffic container (closing TCP connections)')
    assert th.delete_traffic_container('traffic-reproducer-500')

    assert th.read_and_compare_messages('daisy.bgp', 'bgp-01')

    th.transform_log_file('log-01', 'traffic-reproducer-500')
    assert th.check_file_regex_sequence_in_pmacct_log('log-01')
    assert not th.check_regex_in_pmacct_log('ERROR|WARN(?!.*Unable to get kafka_host)')

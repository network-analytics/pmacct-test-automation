
from library.py.test_params import KModuleParams
import logging
import pytest
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(__file__, daemon='nfacctd', ipv6_subnet='cafe::')


@pytest.mark.nfacctd
@pytest.mark.bgp
@pytest.mark.bgp_only
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown)


def main(consumers):
    th = test_tools.KTestHelper(testParams, consumers)
    assert th.spawn_traffic_container('traffic-reproducer-300', detached=True)

    th.set_ignored_fields(['seq', 'timestamp', 'peer_tcp_port'])
    assert th.read_and_compare_messages('daisy.bgp', 'bgp-00')

    th.transform_log_file('log-00', 'traffic-reproducer-300')
    assert th.check_file_regex_sequence_in_pmacct_log('log-00')
    assert not th.check_regex_in_pmacct_log('ERROR|WARN')

    assert th.delete_traffic_container('traffic-reproducer-300')

    th.transform_log_file('log-01', 'traffic-reproducer-300')
    assert th.wait_and_check_logs('log-01', 30, 10)
    assert not th.check_regex_in_pmacct_log('ERROR|WARN(?!.*Unable to get kafka_host)')

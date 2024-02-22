# TODO DAISY:
# - when multi-config execution is supported), add multiple options with path_id/mpls_vpn_rd
#   and also different buckets (per/per_peer buckets) [in this test we have 3 sources and lots of RDs!]

from library.py.test_params import KModuleParams
from library.py.test_helper import KTestHelper
import logging
import pytest
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(__file__, daemon='nfacctd', ipv4_subnet='192.168.100.', ipv6_subnet='cafe::')


@pytest.mark.nfacctd
@pytest.mark.bgp
@pytest.mark.bgp_only
@pytest.mark.basic
def test(test_core, consumer_setup_teardown):
<<<<<<< HEAD
    main(consumer_setup_teardown[0])

def transform_log_file_custom(logfile, repro_ips):
    # repro_ips = [info['repro_ip']  for info in repro_info_list]
    token = secrets.token_hex(4)[:8]
    helpers.replace_in_file(logfile, '${repro_ip}', token)
    test_tools.transform_log_file(logfile)  # the usual log transformations
    helpers.replace_in_file(logfile, token, '(' + '|'.join(repro_ips) + ')')



def main(consumers):
    th = KTestHelper(testParams, consumers)
    test_tools.avoid_time_period_in_seconds(25, 30)

    for suffix in ['a', 'b', 'cd']:
        assert th.spawn_traffic_container('traffic-reproducer-302' + suffix, detached=True)

    th.set_ignored_fields(['seq', 'timestamp', 'peer_tcp_port'])
    assert th.read_and_compare_messages('daisy.bgp', 'bgp-00', 90)

    th.transform_log_file_with_ip('log-00', '172.21.1.1\\d{2}|fd25::1\\d{2}')
    assert th.wait_and_check_logs('log-00', 30, 10)
    assert not th.check_regex_in_pmacct_log('ERROR|WARN(?!(.*Unable to get kafka_host)|(.*Refusing new connection))')

    # Check the capability exchange is there for all three BGP peers:
    # need a check for each as order might change (race condition)
    for log_tag in ['log-01', 'log-02', 'log-03']:
        th.transform_log_file(log_tag, 'traffic-reproducer-302')
        assert th.check_file_regex_sequence_in_pmacct_log(log_tag)

    for suffix in ['a', 'b', 'cd']:
        assert th.delete_traffic_container('traffic-reproducer-302' + suffix)

    # TODO DAISY: - we need to debug why pretag is not working properly on delete messages (bug)
    #                --> until then we check the delete messages excluding the label field
    th.set_ignored_fields(['seq', 'timestamp', 'peer_tcp_port', 'label'])
    assert th.read_and_compare_messages('daisy.bgp', 'bgp-01', 90)

    th.transform_log_file_with_ip('log-04', '172.21.1.1\\d{2}|fd25::1\\d{2}')
    assert th.wait_and_check_logs('log-04', 30, 5)
    # Check logs --> retry each 5s for max 30s as it takes some time to stop traffic-repro containers

    assert not th.check_regex_in_pmacct_log('ERROR|WARN(?!(.*Unable to get kafka_host)|(.*Refusing new connection))')

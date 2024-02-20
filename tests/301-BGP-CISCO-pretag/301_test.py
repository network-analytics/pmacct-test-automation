
from library.py.test_params import KModuleParams
import logging
import pytest
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(__file__, daemon='pmbgpd', ipv4_subnet='192.168.100.')


@pytest.mark.pmbgpd
@pytest.mark.bgp
@pytest.mark.bgp_only
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown)


def main(consumers):
    th = test_tools.KTestHelper(testParams, consumers)
    assert th.spawn_traffic_container('traffic-reproducer-301')

    th.set_ignored_fields(['seq', 'timestamp', 'peer_tcp_port'])
    assert th.read_and_compare_messages('daisy.bgp', 'bgp-00')

    th.transform_log_file('log-00', 'traffic-reproducer-301')
    assert th.wait_and_check_logs('log-00', 30, 10)
    assert not th.check_regex_in_pmacct_log('ERROR|WARN(?!.*Unable to get kafka_host)')






    # assert scripts.replay_pcap(testParams.pcap_folders[0])
    #
    # assert test_tools.read_and_compare_messages(consumer, testParams, 'bgp-00', ['seq', 'timestamp', 'peer_tcp_port'])
    #
    # # Make sure the expected logs exist in pmacct log
    # logfile = testParams.log_files.getFileLike('log-00')
    # test_tools.transform_log_file(logfile, helpers.get_repro_ip_from_pcap_folder(testParams.pcap_folders[0]))
    # assert helpers.retry_until_true('Checking expected logs',
    #                                 lambda: helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file,
    #                                                                                   logfile), 30, 10)
    # assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file,
    #                                                 ['ERROR|WARN(?!.*Unable to get kafka_host)'])

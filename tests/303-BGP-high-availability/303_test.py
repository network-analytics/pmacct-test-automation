
from library.py.test_params import KModuleParams
from library.py.test_helper import KTestHelper
import library.py.helpers as helpers
import library.py.scripts as scripts
import library.py.json_tools as json_tools
import logging
import pytest
import time
import library.py.test_tools as test_tools

logger = logging.getLogger(__name__)

testParams = KModuleParams(__file__, daemon='nfacctd', ipv6_subnet='cafe::')


@pytest.mark.nfacctd
@pytest.mark.bgp
@pytest.mark.bgp_only
@pytest.mark.redis
def test(test_core_redis, consumer_setup_teardown):
    main(consumer_setup_teardown)


def main(consumers):
    th = KTestHelper(testParams, consumers)
    test_tools.avoid_time_period_in_seconds(5, 10)

    # Loading log file into loglines list
    th.transform_log_file('log-00', 'traffic-reproducer-303')
    with open(testParams.log_files.get_item_like('log-00'), 'r') as f:
        loglines = f.read().split('\n')

    # Make sure pmacct instances started in the right order
    assert testParams.pmacct[0].process_name == 'nfacctd_core_loc_A'
    assert testParams.pmacct[1].process_name == 'nfacctd_core_loc_B'
    assert testParams.pmacct[2].process_name == 'nfacctd_core_loc_C'

    assert th.check_regex_sequence_in_pmacct_log([loglines[0], loglines[1]], 'nfacctd-00')
    assert th.check_regex_sequence_in_pmacct_log([loglines[0], loglines[2]], 'nfacctd-01')
    assert th.check_regex_sequence_in_pmacct_log([loglines[0], loglines[2]], 'nfacctd-02')

    assert th.spawn_traffic_container('traffic-reproducer-303', detached=True)

    test_tools.wait_until_second(0)  # wait until mm:00, so that we sync with the traffic reproducer
    test_tools.wait_until_second(15)  # now wait until mm:15, so that BGP connections get established

    assert th.check_regex_in_pmacct_log(loglines[3], 'nfacctd-00')
    assert th.check_regex_in_pmacct_log(loglines[3], 'nfacctd-01')
    assert th.check_regex_in_pmacct_log(loglines[3], 'nfacctd-02')

    assert scripts.send_signal_to_pmacct('nfacctd-00', 'SIGRTMIN')  # Resetting timestamp on A
    time.sleep(2)
    assert th.check_regex_sequence_in_pmacct_log([loglines[4], loglines[2]], 'nfacctd-00')
    assert th.check_regex_in_pmacct_log(loglines[1], 'nfacctd-01')

    time.sleep(5)
    assert scripts.send_signal_to_pmacct('nfacctd-01', 'SIGRTMIN')  # Resetting timestamp on B
    time.sleep(2)
    assert th.check_regex_sequence_in_pmacct_log([loglines[4], loglines[2]], 'nfacctd-01')
    assert th.check_regex_in_pmacct_log(loglines[1], 'nfacctd-02')

    time.sleep(5)
    assert scripts.send_signal_to_pmacct('nfacctd-02', 'SIGRTMIN+1')  # Setting C to forced-active
    time.sleep(2)
    assert th.check_regex_in_pmacct_log(loglines[5], 'nfacctd-02')
    time.sleep(2)
    assert scripts.send_signal_to_pmacct('nfacctd-00', 'SIGRTMIN+2')  # Setting A to forced-standby
    time.sleep(2)
    assert th.check_regex_in_pmacct_log(loglines[6], 'nfacctd-00')
    time.sleep(2)
    assert scripts.send_signal_to_pmacct('nfacctd-01', 'SIGRTMIN+2')  # Setting B to forced-standby
    time.sleep(2)
    assert th.check_regex_in_pmacct_log(loglines[6], 'nfacctd-01')

    time.sleep(5)
    assert scripts.send_signal_to_pmacct('nfacctd-02', 'SIGRTMIN')  # Resetting timestamp on C
    time.sleep(2)
    assert th.check_regex_in_pmacct_log(loglines[8], 'nfacctd-02')
    time.sleep(5)
    assert scripts.send_signal_to_pmacct('nfacctd-00', 'SIGRTMIN+3')  # Setting A to auto-mode
    time.sleep(2)
    assert th.check_regex_sequence_in_pmacct_log([loglines[7], loglines[1]], 'nfacctd-00')

    assert scripts.send_signal_to_pmacct('nfacctd-01', 'SIGRTMIN+3')  # Setting B to auto-mode
    time.sleep(2)
    assert th.check_regex_in_pmacct_log(loglines[7], 'nfacctd-01')

    time.sleep(5)
    assert scripts.send_signal_to_pmacct('nfacctd-02', 'SIGRTMIN+3')  # Setting C to auto-mode
    time.sleep(2)
    assert th.check_regex_sequence_in_pmacct_log([loglines[7], loglines[2]], 'nfacctd-02')

    # Compare received messages to reference file output-bgp-00.json
    messages = consumers[0].get_all_pending_messages()
    output_json_file = test_tools.replace_ips_and_get_reference_file(testParams, 'bgp-00')
    logger.info('Comparing messages received with json lines in file ' + helpers.short_name(output_json_file))
    assert json_tools.compare_messages_to_json_file(messages, output_json_file, ['seq', 'timestamp', 'peer_tcp_port',
                                                                                 'writer_id'], multi_match_allowed=True)

    # Ensuring all three writer_id's show up in the messages
    writer_ids = set([msg['writer_id'] for msg in messages])
    logger.info('There are messages from ' + str(len(writer_ids)) + ' different pmacct processes: ' + str(writer_ids))
    assert len(writer_ids) == 3

    assert not th.check_regex_in_pmacct_log('ERROR|WARN', pmacct_name='nfacctd-00')
    assert not th.check_regex_in_pmacct_log('ERROR|WARN', pmacct_name='nfacctd-01')
    assert not th.check_regex_in_pmacct_log('ERROR|WARN', pmacct_name='nfacctd-02')

    th.delete_traffic_container('traffic-reproducer-303')

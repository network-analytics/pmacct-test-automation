
from library.py.test_params import KModuleParams
import library.py.helpers as helpers
import library.py.scripts as scripts
import logging, pytest, time
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
    test_tools.avoid_time_period_in_seconds(5, 10)
    repro_ip = helpers.get_repro_ip_from_pcap_folder(testParams.pcap_folders[0])

    # Loading log file into loglines list
    logfile = testParams.log_files.getFileLike('log-00')
    test_tools.transform_log_file(logfile, repro_ip)
    with open(logfile, 'r') as f:
        loglines = f.read().split('\n')

    # Make sure pmacct instances started in the right order
    assert testParams.pmacct[0].process_name == 'nfacctd_core_loc_A'
    assert testParams.pmacct[1].process_name == 'nfacctd_core_loc_B'
    assert testParams.pmacct[2].process_name == 'nfacctd_core_loc_C'

    assert helpers.check_regex_sequence_in_file(testParams.pmacct[0].pmacct_log_file, [loglines[0], loglines[1]])
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[1].pmacct_log_file, [loglines[0], loglines[2]])
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[2].pmacct_log_file, [loglines[0], loglines[2]])

    pcap_folder_multi = test_tools.prepare_multicollector_pcap_player(testParams.results_folder,
        testParams.pcap_folders[0], testParams.pmacct, testParams.fw_config)
    assert pcap_folder_multi
    # Play traffic against all 3 nfacctd instances
    assert scripts.replay_pcap_detached(pcap_folder_multi)

    # Read 5 messages. Required because otherwise the log message about "BGP peers usage 1/100" does not appear
    messages = consumers[0].get_messages(65, 5)
    assert messages!=None and messages[0]['writer_id']==testParams.pmacct[0].process_name  # 'nfacctd_core_loc_A'

    time.sleep(5)
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[0].pmacct_log_file, [loglines[3]])
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[1].pmacct_log_file, [loglines[3]])
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[2].pmacct_log_file, [loglines[3]])

    assert scripts.send_signal_to_pmacct(testParams.pmacct[0].name, 'SIGRTMIN')  # Resetting timestamp on A
    time.sleep(2)
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[0].pmacct_log_file, [loglines[4], loglines[2]])
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[1].pmacct_log_file, [loglines[1]])

    time.sleep(5)
    assert scripts.send_signal_to_pmacct(testParams.pmacct[1].name, 'SIGRTMIN')  # Resetting timestamp on B
    time.sleep(2)
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[1].pmacct_log_file, [loglines[4], loglines[2]])
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[2].pmacct_log_file, [loglines[1]])

    time.sleep(5)
    assert scripts.send_signal_to_pmacct(testParams.pmacct[2].name, 'SIGRTMIN+1')  # Setting C to forced-active
    time.sleep(2)
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[2].pmacct_log_file, [loglines[5]])
    time.sleep(2)
    assert scripts.send_signal_to_pmacct(testParams.pmacct[0].name, 'SIGRTMIN+2')  # Setting A to forced-standby
    time.sleep(2)
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[0].pmacct_log_file, [loglines[6]])
    time.sleep(2)
    assert scripts.send_signal_to_pmacct(testParams.pmacct[1].name, 'SIGRTMIN+2')  # Setting B to forced-standby
    time.sleep(2)
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[1].pmacct_log_file, [loglines[6]])

    time.sleep(5)
    assert scripts.send_signal_to_pmacct(testParams.pmacct[2].name, 'SIGRTMIN')  # Resetting timestamp on C
    time.sleep(2)
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[2].pmacct_log_file, [loglines[8]])

    time.sleep(5)
    assert scripts.send_signal_to_pmacct(testParams.pmacct[0].name, 'SIGRTMIN+3')  # Setting A to auto-mode
    time.sleep(2)
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[0].pmacct_log_file, [loglines[7], loglines[1]])

    assert scripts.send_signal_to_pmacct(testParams.pmacct[1].name, 'SIGRTMIN+3')  # Setting B to auto-mode
    time.sleep(2)
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[1].pmacct_log_file, [loglines[7]])

    time.sleep(5)
    assert scripts.send_signal_to_pmacct(testParams.pmacct[2].name, 'SIGRTMIN+3')  # Setting C to auto-mode
    time.sleep(2)
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[2].pmacct_log_file, [loglines[7], loglines[2]])

    scripts.stop_and_remove_traffic_container(testParams.pcap_folders[0])

    assert test_tools.read_and_compare_all_messages(consumers[0], testParams, 'bgp-00',
                                                ['seq', 'timestamp', 'peer_tcp_port', 'writer_id'], messages)

    assert not helpers.check_regex_sequence_in_file(testParams.pmacct[0].pmacct_log_file, ['ERROR|WARN'])
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct[1].pmacct_log_file, ['ERROR|WARN'])
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct[2].pmacct_log_file, ['ERROR|WARN'])

    # only_loc_A = True
    # # Checking if at least one message was sent by a pmacct instance other than nfacctd-00/nfacctd_core_loc_A
    # for message in messages:
    #     if message['writer_id'] != testParams.pmacct[0].process_name:
    #         only_loc_A = False
    #         break
    # assert not only_loc_A

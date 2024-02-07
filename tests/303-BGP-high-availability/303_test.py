
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

    logfile = testParams.log_files.getFileLike('log-00')
    test_tools.transform_log_file(logfile, repro_ip)
    with open(logfile, 'r') as f:
        loglines = f.read().split('\n')

    assert helpers.check_regex_sequence_in_file(testParams.pmacct[0].pmacct_log_file, [loglines[0], loglines[1]])
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[1].pmacct_log_file, [loglines[0], loglines[2]])
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[2].pmacct_log_file, [loglines[0], loglines[2]])

    pcap_folder_multi = test_tools.prepare_multicollector_pcap_player(testParams.results_folder,
        testParams.pcap_folders[0], testParams.pmacct, testParams.fw_config)
    assert pcap_folder_multi
    # Play traffic against all 3 nfacctd instances
    assert scripts.replay_pcap_detached(pcap_folder_multi)
    # Read messages for one minute --- messages should refer to first nfacctd instance "locA"
    assert test_tools.read_messages_dump_only(consumers.getReaderOfTopicStartingWith('daisy.bgp'), testParams, 60)

    time.sleep(5)

    assert helpers.check_regex_sequence_in_file(testParams.pmacct[0].pmacct_log_file, [loglines[3]])
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[1].pmacct_log_file, [loglines[3]])
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[2].pmacct_log_file, [loglines[3]])

    assert scripts.send_signal_to_pmacct(testParams.pmacct[0].name, 'SIGRTMIN')

    time.sleep(2)

    assert helpers.check_regex_sequence_in_file(testParams.pmacct[0].pmacct_log_file, [loglines[4], loglines[2]])
    assert helpers.check_regex_sequence_in_file(testParams.pmacct[1].pmacct_log_file, [loglines[1]])

    return True

    # Prepare the multicast pcap player (mount points, traffic-repro.yml, docker-compose.yml, etc.)
    pcap_folder_multi = test_tools.prepare_multicollector_pcap_player(testParams.results_folder, testParams.pcap_folders[0],
        testParams.pmacct, testParams.fw_config)
    assert pcap_folder_multi
    # Play traffic against all 3 nfacctd instances
    assert scripts.replay_pcap_detached(pcap_folder_multi)
    # Read messages for one minute --- messages should refer to first nfacctd instance "locA"
    assert test_tools.read_messages_dump_only(consumers.getReaderOfTopicStartingWith('daisy.bgp'), testParams, 60)
    # Reset timer of nfacctd-00
    assert scripts.send_signal_to_pmacct(testParams.pmacct[0].name, 'SIGRTMIN')
    # Read messages for a while --- message should now refer to second nfacctd instance "locB"
    assert test_tools.read_messages_dump_only(consumers.getReaderOfTopicStartingWith('daisy.bgp'), testParams, 40)

    scripts.stop_and_remove_traffic_container(testParams.pcap_folders[0])



# def main(consumers):
#     pcap_folder_multi = test_tools.prepare_multicast_pcap_player(testParams.results_folder, testParams.pcap_folders[0],
#         testParams.pmacct, 0, testParams.fw_config)
#     assert pcap_folder_multi
#     assert scripts.replay_pcap_detached(pcap_folder_multi)
#
#     # assert test_tools.replay_pcap_to_collector(testParams.pcap_folders[0], testParams.pmacct[0], True)
#     repro_ip = helpers.get_repro_ip_from_pcap_folder(testParams.pcap_folders[0])
#     logger.debug('Repro IP: ' + repro_ip)
#     assert test_tools.read_messages_dump_only(consumers.getReaderOfTopicStartingWith('daisy.bgp'), testParams)
#     scripts.stop_and_remove_traffic_container(testParams.pcap_folders[0])
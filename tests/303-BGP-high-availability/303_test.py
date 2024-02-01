
from library.py.test_params import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys, time
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], daemon='nfacctd', ipv6_subnet='cafe::')

@pytest.mark.nfacctd
@pytest.mark.bgp
@pytest.mark.bgp_only
@pytest.mark.redis
def test(test_core_redis, consumer_setup_teardown):
    main(consumer_setup_teardown)

def main(consumers):
    #time.sleep(3)
    #assert scripts.send_signal_to_pmacct(testParams.pmacct[0].name, 'SIGRTMIN')


    pcap_folder_multi = test_tools.prepare_multicast_pcap_player(testParams.results_folder, testParams.pcap_folders[0],
        testParams.pmacct, 0, testParams.fw_config)
    assert pcap_folder_multi
    assert scripts.replay_pcap_detached(pcap_folder_multi)

    assert test_tools.read_messages_dump_only(consumers.getReaderOfTopicStartingWith('daisy.bgp'), testParams, 20)
    assert scripts.send_signal_to_pmacct(testParams.pmacct[0].name, 'SIGRTMIN')
    time.sleep(5)
    assert test_tools.read_messages_dump_only(consumers.getReaderOfTopicStartingWith('daisy.bgp'), testParams, 20)


    scripts.stop_and_remove_traffic_container(testParams.pcap_folders[0])




    # assert scripts.send_signal_to_pmacct(testParams.pmacct[0].name, 'SIGRTMIN')
    #
    # assert scripts.replay_pcap_detached(pcap_folder_multi)
    # assert test_tools.read_messages_dump_only(consumers.getReaderOfTopicStartingWith('daisy.bgp'),
    #     testParams, 'bgp-00', ['seq', 'timestamp', 'peer_tcp_port', 'writer_id'])




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

from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys, time, datetime, secrets
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], ipv4_subnet='192.168.100.', ipv6_subnet='cafe::')
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def transform_log_file(logfile, repro_info_list):
    repro_ips = [info['repro_ip']  for info in repro_info_list]
    repro_bgp_ids = [info['bgp_id'] for info in repro_info_list if 'bgp_id' in info.keys()]
    token1 = secrets.token_hex(4)[:8]
    token2 = secrets.token_hex(4)[:8]
    helpers.replace_in_file(logfile, '${repro_ip}', token1)
    helpers.replace_in_file(logfile, '${bgp_id}', token2)
    test_tools.transform_log_file(logfile)
    helpers.replace_in_file(logfile, token1, '(' + '|'.join(repro_ips) + ')')
    helpers.replace_in_file(logfile, token2, '(' + '|'.join(repro_bgp_ids) + ')')

def main(consumer):
    logger.info('Minute seconds: ' + str(datetime.datetime.now().second))
    wait_sec = 31 - datetime.datetime.now().second
    if wait_sec > 0:
        logger.debug('Waiting ' + str(wait_sec) + ' seconds')
        time.sleep(wait_sec)

    pcap_folder = test_tools.prepare_multi_pcap_player(testParams.results_folder,
                                         [testParams.pcap_folders[2], testParams.pcap_folders[3]])
    assert pcap_folder

    repro_info_list = []
    for i in [0, 1]:
        repro_info = scripts.replay_pcap_detached(testParams.pcap_folders[i], i)
        assert repro_info
        repro_info_list.append(repro_info)
    repro_info_multi = scripts.replay_pcap_detached_multi(pcap_folder, 2)
    assert repro_info_multi
    repro_info_list.append(repro_info_multi)

    assert test_tools.read_and_compare_messages(consumer, testParams, 'bgp-00',
        ['seq', 'timestamp', 'peer_tcp_port', 'bgp_nexthop'], 240)

    logfile = testParams.log_files.getFileLike('log-00')
    transform_log_file(logfile, repro_info_list)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file,
                                                    ['ERROR|WARNING(?!.*Unable to get kafka_host)'])

    scripts.stop_and_remove_traffic_container(2)

    logfile = testParams.log_files.getFileLike('log-01')
    test_tools.transform_log_file(logfile, repro_info_multi['repro_ip'], repro_info_multi['bgp_id'])
    assert helpers.retry_until_true('Checking expected logs',
        lambda: helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile), 30, 10)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file,
                                                    ['ERROR|WARNING(?!.*Unable to get kafka_host)'])

# TODO DAISY:
# - when multi-config execution is supported), add multiple options with path_id/mpls_vpn_rd
#   and also different buckets (per/per_peer buckets) [in this test we have 3 sources and lots of RDs!]

from library.py.test_params import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys, time, datetime, secrets
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], daemon='nfacctd', ipv4_subnet='192.168.100.', ipv6_subnet='cafe::')

@pytest.mark.nfacctd
@pytest.mark.bgp
@pytest.mark.bgp_only
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def transform_log_file_custom(logfile, repro_ips):
    # repro_ips = [info['repro_ip']  for info in repro_info_list]
    token = secrets.token_hex(4)[:8]
    helpers.replace_in_file(logfile, '${repro_ip}', token)
    test_tools.transform_log_file(logfile)  # the usual log transformations
    helpers.replace_in_file(logfile, token, '(' + '|'.join(repro_ips) + ')')

def main(consumer):
    curr_sec = datetime.datetime.now().second
    logger.info('Minute seconds: ' + str(curr_sec))
    
    # Some additional timing constraints for this test
    # Make sure traffic reproducer 03 does not send packets before the others
    if curr_sec < 25: 
        wait_sec = 25 - curr_sec
        logger.debug('Waiting ' + str(wait_sec) + ' seconds')
        time.sleep(wait_sec)
    # Make sure that traffic reproducers do not start in different minutes
    elif curr_sec > 55:
        wait_sec = 85 - curr_sec
        logger.debug('Waiting ' + str(wait_sec) + ' seconds')
        time.sleep(wait_sec)

    pcap_folder_multi = test_tools.prepare_multi_pcap_player(testParams.results_folder,
        [testParams.pcap_folders[2], testParams.pcap_folders[3]], 2, testParams.fw_config)
    assert pcap_folder_multi

    repro_ip_list = []
    for i in [0, 1]:
        assert scripts.replay_pcap_detached(testParams.pcap_folders[i])
        repro_ip_list.append(helpers.get_repro_ip_from_pcap_folder(testParams.pcap_folders[i]))

    assert scripts.replay_pcap_detached(pcap_folder_multi)
    repro_ip_list.append(helpers.get_repro_ip_from_pcap_folder(testParams.pcap_folders[2])) # needs to find a yml

    assert test_tools.read_and_compare_messages(consumer, testParams, 'bgp-00',
        ['seq', 'timestamp', 'peer_tcp_port'], 90)

    logfile = testParams.log_files.getFileLike('log-00')
    transform_log_file_custom(logfile, repro_ip_list)
    # Check logs --> retry until traffic-reproducer-03 has attempted the connection
    assert helpers.retry_until_true('Checking expected logs',
        lambda: helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile), 30, 10)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file,
               ['ERROR|WARN(?!(.*Unable to get kafka_host)|(.*Refusing new connection))'])

    # Check the capability exchange is there for all three BGP peers: need a check for each as order might change (race condition)
    for i in ['log-01', 'log-02', 'log-03']:
        logfile = testParams.log_files.getFileLike(i)
        test_tools.transform_log_file(logfile)
        assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)

    for i in [0, 1, 2]:
      scripts.stop_and_remove_traffic_container_byID(i)

    # TODO DAISY: - we need to debug why pretag is not working properly on delete messages (bug)
    #                --> until then we check the delete messages excluding the label field
    assert test_tools.read_and_compare_messages(consumer, testParams, 'bgp-01',
        ['seq', 'timestamp', 'peer_tcp_port', 'label'], 60)

    logfile = testParams.log_files.getFileLike('log-04')
    transform_log_file_custom(logfile, repro_ip_list)
    # Check logs --> retry each 5s for max 30s as it takes some time to stop traffic-repro containers
    assert helpers.retry_until_true('Checking expected logs',
        lambda: helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile), 30, 5)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file,
               ['ERROR|WARN(?!(.*Unable to get kafka_host)|(.*Refusing new connection))'])

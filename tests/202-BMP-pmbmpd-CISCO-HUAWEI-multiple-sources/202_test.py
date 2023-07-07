
from library.py.configuration_file import KConfigurationFile
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys, time
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], pmacct_config_filename='pmbmpd-00.conf')
confFile = KConfigurationFile(testParams.test_conf_file)

def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, pmacct_setup_teardown, prepare_pcap, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def main(consumer):
    for i in range(len(testParams.results_pcap_folders)):
        assert scripts.replay_pcap_with_detached_docker(testParams.results_pcap_folders[i], i, '172.111.1.' + str(100+i+1))

    assert test_tools.read_and_compare_messages(consumer, testParams.output_files.getFileLike('bmp-00'),
        [('192.168.100.1', '172.111.1.101'), ('192.168.100.2', '172.111.1.102'), ('192.168.100.3', '172.111.1.103')],
        ['seq', 'timestamp', 'timestamp_arrival', 'bmp_router_port', 'bgp_nexthop'])  # bgp_nexthop is wrong (?)

    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, testParams.log_files.getFileLike('log-00'))
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING'])

    for i in range(len(testParams.results_pcap_folders)):
        scripts.stop_and_remove_traffic_container(i)

    logger.debug('Waiting 10 sec')
    time.sleep(10)  # needed for the last regex (WARNING) to be found in the logs!

    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, testParams.log_files.getFileLike('log-01'))
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING(?!.*Unable to get kafka_host)'])

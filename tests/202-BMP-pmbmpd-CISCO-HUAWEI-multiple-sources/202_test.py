
from library.py.configuration_file import KConfigurationFile
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys, time
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], pmacct_config_filename='pmbmpd-00.conf')

def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, pmacct_setup_teardown, prepare_pcap, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def transform_log_file(logfile):
    helpers.replace_in_file(logfile, '${repro_ip}', 'ABCDEFGH')
    test_tools.transform_log_file(logfile)
    helpers.replace_in_file(logfile, "ABCDEFGH", '172.111.1.1\\d{2}')

def main(consumer):
    for i in range(len(testParams.pcap_folders)):
        assert scripts.replay_pcap_detached(testParams.pcap_folders[i], i)

    assert test_tools.read_and_compare_messages(consumer, testParams.output_files.getFileLike('bmp-00'),
        [('192.168.100.1', '172.111.1.101'), ('192.168.100.2', '172.111.1.102'), ('192.168.100.3', '172.111.1.103')],
        ['seq', 'timestamp', 'timestamp_arrival', 'bmp_router_port', 'bgp_nexthop'])  # bgp_nexthop is wrong (?)

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-00')
    transform_log_file(logfile)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING(?!.*Unable to get kafka_host)'])

    for i in range(len(testParams.pcap_folders)):
        scripts.stop_and_remove_traffic_container(i)

    logger.debug('Waiting 10 sec')
    time.sleep(10)  # needed for the last regex (WARNING) to be found in the logs!

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-01')
    transform_log_file(logfile)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING(?!.*Unable to get kafka_host)'])

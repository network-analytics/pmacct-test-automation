
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys, time
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], ipv4_subnet='192.168.100.')

def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def main(consumer):
    assert scripts.replay_pcap(testParams.pcap_folders[0])

    assert test_tools.read_and_compare_messages(consumer, testParams, 'bmp-00',
        ['seq', 'timestamp', 'timestamp_arrival', 'bmp_router_port', 'bgp_nexthop'])  # bgp_nexthop ?)

    # Make sure the expected logs exist in pmacct log
    logger.info('Waiting 15 seconds')
    time.sleep(15)  # needed for the last regex (WARNING) to be found in the logs!

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-00')
    helpers.replace_in_file(logfile, '/etc/pmacct/librdkafka.conf', testParams.pmacct_mount_folder + '/librdkafka.conf')
    test_tools.transform_log_file(logfile, '172.111.1.101')
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING(?!.*Unable to get kafka_host)'])


# Underscore prevents the test from being run by pytest
# For troubleshooting: sets up kafka infra and pmacct
def t_est_start_pmacct(check_root_dir, kafka_infra_setup, prepare_test, prepare_config_local, prepare_pcap, pmacct_setup):
    assert True

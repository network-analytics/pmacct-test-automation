
from library.py.configuration_file import KConfigurationFile
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys, time
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__])
confFile = KConfigurationFile(testParams.test_conf_file)

def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, pmacct_setup_teardown, prepare_pcap, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def main(consumer):
    assert scripts.replay_pcap_with_docker(testParams.results_pcap_folders[0], '172.111.1.101')

    assert test_tools.read_and_compare_messages(consumer, testParams.output_files.getFileLike('bmp-00'),
        [('192.168.100.1', '172.111.1.101')],
        ['seq', 'timestamp', 'timestamp_arrival', 'bmp_router_port', 'bgp_nexthop'])  # bgp_nexthop ?)

    # Make sure the expected logs exist in pmacct log
    logger.info('Waiting 15 seconds')
    time.sleep(15)  # needed for the last regex (WARNING) to be found in the logs!
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, testParams.log_files.getFileLike('log-00'))
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING(?!.*Unable to get kafka_host)'])


# Underscore prevents the test from being run by pytest
# For troubleshooting: sets up kafka infra and pmacct
def t_est_start_pmacct(check_root_dir, kafka_infra_setup, prepare_test, prepare_config_local, prepare_pcap, pmacct_setup):
    assert True

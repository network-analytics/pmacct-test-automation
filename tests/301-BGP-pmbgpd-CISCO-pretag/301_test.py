
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys, time
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], pmacct_config_filename='pmbgpd-00.conf')

def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def main(consumer):
    assert scripts.replay_pcap(testParams.pcap_folders[0])

    assert test_tools.read_and_compare_messages(consumer, testParams.output_files.getFileLike('bgp-00'),
        [('192.168.100.1', '172.111.1.101')], ['seq', 'timestamp', 'peer_tcp_port'])

    # Make sure the expected logs exist in pmacct log
    logger.info('Waiting 15 seconds')
    time.sleep(15)  # needed for the last regex (WARNING) to be found in the logs!
    # assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, testParams.log_files.getFileLike('log-00'))
    # assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING(?!.*Unable to get kafka_host)'])

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-00')
    test_tools.transform_log_file(logfile, '172.111.1.101', testParams.bgp_id)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING(?!.*Unable to get kafka_host)'])

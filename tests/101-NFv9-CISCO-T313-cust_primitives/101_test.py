
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys, time
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__])

def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def main(consumer):
    assert scripts.replay_pcap(testParams.pcap_folders[0])

    assert test_tools.read_and_compare_messages(consumer, testParams.output_files.getFileLike('flow-00'),
        [('192.168.100.1', '172.111.1.101')],
        ['timestamp_start', 'timestamp_end', 'timestamp_arrival', 'timestamp_min', 'timestamp_max',
         'stamp_inserted', 'stamp_updated'])

    #assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING'])
    logger.info('Waiting 15 seconds')
    time.sleep(15)  # needed for the last message ('Purging cache - END (PID: xx, QN: 51/51, ET: 0)') to exist in logs
    #assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, testParams.log_files.getFileLike('log-00'))

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-00')
    test_tools.transform_log_file(logfile)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING'])


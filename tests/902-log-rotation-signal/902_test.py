import os

from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import time, logging, pytest, sys
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], daemon='nfacctd', ipv4_subnet='192.168.100.')

@pytest.mark.nfacctd
@pytest.mark.signals
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def main(consumer):
    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-00')
    test_tools.transform_log_file(logfile)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN'])

    os.rename(testParams.pmacct_log_file, testParams.pmacct_log_file + '.bak')
    assert not os.path.isfile(testParams.pmacct_log_file)
    logger.info('Log file deleted')

    #logger.debug('SEND SIGHUP SIGNAL (Waiting 180 sec)')
    #time.sleep(180)

    # Sending the signal to recreate log file
    assert scripts.send_signal_to_pmacct('SIGHUP')

    logger.debug('Waiting 65 sec')
    time.sleep(65)

    assert os.path.isfile(testParams.pmacct_log_file)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)


from library.py.test_params import KModuleParams
from library.py.test_helper import KTestHelper
import time
import logging
import pytest
import os
logger = logging.getLogger(__name__)

testParams = KModuleParams(__file__, daemon='nfacctd', ipv4_subnet='192.168.100.')


@pytest.mark.nfacctd
@pytest.mark.signals

@pytest.mark.xfail  # Expected to fail due to signals not going through with docker images
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown)


def main(consumers):
    th = KTestHelper(testParams, consumers)

    th.transform_log_file('log-00')
    assert th.check_file_regex_sequence_in_pmacct_log('log-00')
    assert not th.check_regex_in_pmacct_log('ERROR|WARN')

    os.rename(testParams.pmacct_log_file, testParams.pmacct_log_file + '.bak')
    assert not os.path.isfile(testParams.pmacct_log_file)
    logger.info('Log file deleted')

    # logger.debug('SEND SIGHUP SIGNAL (Waiting 180 sec)')
    # time.sleep(180)

    # Sending the signal to recreate log file
    assert th.send_signal_to_pmacct('SIGHUP')

    logger.debug('Waiting 65 sec')
    time.sleep(65)

    assert os.path.isfile(testParams.pmacct_log_file)
    assert th.check_file_regex_sequence_in_pmacct_log('log-00')

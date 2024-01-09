
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys, time, datetime
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__])

@pytest.mark.ipfix
@pytest.mark.ipfix_only
@pytest.mark.ipfixv10
@pytest.mark.nfv9
@pytest.mark.avro
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def main(consumer):
    # Make sure that traffic reproducers do not start in different minutes
    curr_sec = datetime.datetime.now().second
    logger.info('Minute seconds: ' + str(curr_sec))
    if curr_sec > 55:
        wait_sec = 85 - curr_sec
        logger.debug('Waiting ' + str(wait_sec) + ' seconds')
        time.sleep(wait_sec)

    for i in range(len(testParams.pcap_folders)):
        assert scripts.replay_pcap_detached(testParams.pcap_folders[i], i)

    assert test_tools.read_and_compare_messages(consumer, testParams, 'flow-00',
        ['timestamp_arrival', 'timestamp_min', 'timestamp_max', 'stamp_inserted', 'stamp_updated'])

    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN'])

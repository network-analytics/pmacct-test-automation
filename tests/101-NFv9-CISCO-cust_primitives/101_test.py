
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], daemon='nfacctd', ipv4_subnet='192.168.100.')

@pytest.mark.nfacctd
@pytest.mark.ipfix
@pytest.mark.ipfix_only
@pytest.mark.nfv9
@pytest.mark.avro
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def main(consumer):
    assert scripts.replay_pcap(testParams.pcap_folders[0])

    assert test_tools.read_and_compare_messages(consumer, testParams, 'flow-00',
        ['timestamp_arrival', 'timestamp_min', 'timestamp_max',
         'stamp_inserted', 'stamp_updated'])

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-00')
    test_tools.transform_log_file(logfile)

    # Retry needed for the last message ('Purging cache - END (PID: xx, QN: 51/51, ET: 0)') to exist in logs
    assert helpers.retry_until_true('Checking expected logs',
        lambda: helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile), 30, 10)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN'])

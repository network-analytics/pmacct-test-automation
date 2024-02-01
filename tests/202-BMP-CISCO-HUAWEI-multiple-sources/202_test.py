
from library.py.test_params import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys, secrets
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], daemon='pmbmpd', ipv4_subnet='192.168.100.')

@pytest.mark.pmbmpd
@pytest.mark.bmp
@pytest.mark.bmp_only
@pytest.mark.bmpv3
@pytest.mark.basic
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def transform_log_file_custom(logfile):
    token = secrets.token_hex(4)[:8]
    helpers.replace_in_file(logfile, '${repro_ip}', token)
    test_tools.transform_log_file(logfile)
    helpers.replace_in_file(logfile, token, '172.21.1.1\\d{2}') # we don't really know which one will come first

def main(consumer):
    for i in range(len(testParams.pcap_folders)):
        assert scripts.replay_pcap_detached(testParams.pcap_folders[i])

    assert test_tools.read_and_compare_messages(consumer, testParams, 'bmp-00',
        ['seq', 'timestamp', 'timestamp_arrival', 'bmp_router_port'])

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-00')
    transform_log_file_custom(logfile)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['\\[172\\.21\\.1\\.101] BMP peers usage'])
    assert helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['\\[172\\.21\\.1\\.102] BMP peers usage'])
    assert helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['\\[172\\.21\\.1\\.103] BMP peers usage'])
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN(?!.*Unable to get kafka_host)'])

    for folder in testParams.pcap_folders:
        scripts.stop_and_remove_traffic_container(folder)

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-01')
    transform_log_file_custom(logfile)

    # Retry needed for the last regex (WARN) to be found in the logs!
    assert helpers.retry_until_true('Checking expected logs',
        lambda: helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile), 30, 10)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN(?!.*Unable to get kafka_host)'])


from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], ipv4_subnet='192.168.100.')

def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def transform_log_file(logfile, repro_ip):
    helpers.replace_in_file(logfile, '/etc/pmacct/librdkafka.conf', testParams.pmacct_mount_folder + '/librdkafka.conf')
    test_tools.transform_log_file(logfile, repro_ip)

def main(consumer):
    repro_info = scripts.replay_pcap(testParams.pcap_folders[0])
    assert repro_info

    assert test_tools.read_and_compare_messages(consumer, testParams, 'bmp-00',
        ['seq', 'timestamp', 'timestamp_arrival', 'bmp_router_port'])

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-00')
    transform_log_file(logfile, repro_info['repro_ip'])

    # Retry needed for the last regex (WARN) to be found in the logs!
    assert helpers.retry_until_true('Checking expected logs',
        lambda: helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile), 30, 10)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN(?!.*Unable to get kafka_host)'])

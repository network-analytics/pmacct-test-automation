
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], ipv4_subnet='192.168.100.')

@pytest.mark.ipfix
@pytest.mark.bgp
def test(test_core_no_kafka, consumer_setup_teardown):
    main(consumer_setup_teardown)

def main(consumers):
    assert scripts.replay_pcap_detached(testParams.pcap_folders[0], 0)
    repro_ip = helpers.get_repro_ip_from_pcap_folder(testParams.pcap_folders[0])

    assert test_tools.read_and_compare_messages(consumers.getReaderOfTopicStartingWith('daisy.bgp'),
        testParams, 'bgp-00',
        ['seq', 'timestamp', 'timestamp_arrival', 'peer_tcp_port'])

    assert test_tools.read_and_compare_messages(consumers.getReaderOfTopicStartingWith('daisy.flow'),
        testParams, 'flow-00',
        ['stamp_inserted', 'stamp_updated', 'timestamp_max', 'timestamp_arrival', 'timestamp_min'])

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-00')
    test_tools.transform_log_file(logfile, repro_ip)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN'])

    logger.info('Stopping traffic container (closing TCP connections)')
    assert scripts.stop_and_remove_traffic_container(testParams.pcap_folders[0])

    assert test_tools.read_and_compare_messages(consumers.getReaderOfTopicStartingWith('daisy.bgp'),
        testParams, 'bgp-01', ['seq', 'timestamp', 'timestamp_arrival', 'peer_tcp_port'])

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-01')
    test_tools.transform_log_file(logfile, repro_ip)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN(?!.*Unable to get kafka_host)'])

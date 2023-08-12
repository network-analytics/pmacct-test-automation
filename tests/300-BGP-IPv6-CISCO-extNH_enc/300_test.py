
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], ipv6_subnet='cafe::')

def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown)

def main(consumers):
    repro_info = scripts.replay_pcap_detached(testParams.pcap_folders[0], 0)
    assert repro_info

    assert test_tools.read_and_compare_messages(consumers.getReaderOfTopicStartingWith('daisy.bgp'),
        testParams, 'bgp-00', ['seq', 'timestamp', 'bgp_nexthop', 'peer_tcp_port'])

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-00')
    test_tools.transform_log_file(logfile, repro_info['repro_ip'], repro_info['bgp_id'])
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING(?!.*Unable to get kafka_host)'])

    scripts.stop_and_remove_traffic_container(0)

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-01')
    test_tools.transform_log_file(logfile, repro_info['repro_ip'], repro_info['bgp_id'])
    # Retry needed for the last regex (WARNING) to be found in the logs
    assert helpers.retry_until_true('Checking expected logs',
        lambda: helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile), 30, 10)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING(?!.*Unable to get kafka_host)'])

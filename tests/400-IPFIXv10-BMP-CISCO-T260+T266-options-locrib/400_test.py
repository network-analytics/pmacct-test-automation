
from library.py.configuration_file import KConfigurationFile
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.json_tools as jsontools
import library.py.helpers as helpers
import os, logging, pytest, sys, time
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__])
confFile = KConfigurationFile(testParams.test_conf_file)

def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, pmacct_setup_teardown, prepare_pcap, consumer_setup_teardown):
    main(consumer_setup_teardown)

def main(consumers):
    assert scripts.replay_pcap_with_detached_docker(testParams.results_pcap_folders[0], 0, '172.111.1.101')

    # Replace peer_ip_src with the correct IP address
    for filename in testParams.output_files:
        helpers.replace_in_file(filename, '192.168.100.1', '172.111.1.101')

    assert test_tools.read_and_compare_messages(consumers.getReaderOfTopicStartingWith('daisy.flow'),
        testParams.output_files.getFileLike('flow-00'), [('192.168.100.1', '172.111.1.101')],
        ['stamp_inserted', 'stamp_updated', 'timestamp_max', 'timestamp_arrival', 'timestamp_min'])

    assert test_tools.read_and_compare_messages(consumers.getReaderOfTopicStartingWith('daisy.bmp'),
        testParams.output_files.getFileLike('bmp-00'), [('192.168.100.1', '172.111.1.101')],
        ['seq', 'timestamp', 'timestamp_arrival', 'bmp_router_port', 'bgp_nexthop'])

    # Make sure the expected logs exist in pmacct log
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, testParams.log_files.getFileLike('log-00'))
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING(?!.*Unable to get kafka_host)'])

    logger.info('Waiting 10 sec')
    time.sleep(10)

    logger.info('Stopping traffic container (closing TCP connections)')
    assert scripts.stop_and_remove_traffic_container(0)

    assert test_tools.read_and_compare_messages(consumers.getReaderOfTopicStartingWith('daisy.bmp'),
        testParams.output_files.getFileLike('bmp-01'), [('192.168.100.1', '172.111.1.101')],
        ['seq', 'timestamp', 'timestamp_arrival', 'bmp_router_port', 'bgp_nexthop'])

    # Make sure the expected logs exist in pmacct log
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, testParams.log_files.getFileLike('log-01'))
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING(?!.*Unable to get kafka_host)'])

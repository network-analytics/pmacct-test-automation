
from library.py.configuration_file import KConfigurationFile
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.json_tools as jsontools
import library.py.helpers as helpers
import os, logging, pytest, sys, json, time
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__])
confFile = KConfigurationFile(testParams.test_conf_file)

def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, pmacct_setup_teardown, prepare_pcap, consumer_setup_teardown):
    main(consumer_setup_teardown)

def main(consumer):
    assert scripts.replay_pcap_with_docker(testParams.results_pcap_folders[0], '172.111.1.101')
    messages = consumer.get_messages(120, helpers.count_non_empty_lines(testParams.results_output_files[0])) # 51 lines
    assert messages != None and len(messages) > 0

    logger.info('Waiting 15 seconds')
    time.sleep(15)  # needed for the last message ('Purging cache - END (PID: xx, QN: 51/51, ET: 0)') to exist in logs

    assert not helpers.check_regex_sequence_in_file(testParams.results_log_file, ['ERROR|WARNING'])

    # Replace peer_ip_src with the actual IP address in output-xyz.json
    helpers.replace_in_file(testParams.results_output_files[0], '192.168.100.1', '172.111.1.101')

    # Compare received json messages to output-flow-00.json
    ignore_fields = ['timestamp_start', 'timestamp_end', 'timestamp_arrival', 'timestamp_min',
                     'timestamp_max', 'stamp_inserted', 'stamp_updated']
    assert jsontools.compare_messages_to_json_file(messages, testParams.results_output_files[0], ignore_fields)

    # Make sure the expected logs exist in pmacct log
    assert helpers.check_file_regex_sequence_in_file(testParams.results_log_file, testParams.results_log_files[0])

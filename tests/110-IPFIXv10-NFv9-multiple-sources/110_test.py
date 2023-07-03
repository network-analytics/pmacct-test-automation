
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
    for i in range(len(testParams.results_pcap_folders)):
        assert scripts.replay_pcap_with_detached_docker(testParams.results_pcap_folders[i], i, '172.111.1.' + str(100+i+1))
    messages = consumer.get_messages(120, helpers.count_non_empty_lines(testParams.output_files[0])) # 98 lines
    assert messages!=None and len(messages) > 0

    logger.debug('Waiting 10 sec')
    time.sleep(10) # needed for the last regex (WARNING) to be found in the logs!

    # Comparing received json messages to output-flow-00.json
    # No IP substitution in json file is done, since we don't know which IP (of the three) will yield which message
    ignore_fields = ['timestamp_max', 'timestamp_arrival', 'stamp_inserted', 'timestamp_min', 'stamp_updated',
                     'timestamp_start', 'timestamp_end',
                     'peer_ip_src']  # Needed since we didn't substitute the IPs
    assert jsontools.compare_messages_to_json_file(messages, testParams.output_files[0], ignore_fields)

    # Check for ERRORs or WARNINGs (but not the warning we want)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING'])


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
    messages = consumer.get_messages(120, helpers.count_non_empty_lines(testParams.results_output_files[0])) # 132 lines
    assert messages != None and len(messages) > 0

    logger.info('Waiting 15 seconds')
    time.sleep(15) # needed for the last regex (WARNING) to be found in the logs!

    # Make sure the expected logs exist in pmacct log
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, testParams.results_log_files[0])
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING(?!.*Unable to get kafka_host)'])

    # Replace peer_ip_src with the correct IP address
    helpers.replace_in_file(testParams.results_output_files[0], '192.168.100.1', '172.111.1.101')

    ignore_fields = ['seq', 'timestamp', 'timestamp_arrival', 'bmp_router_port',
                     'bgp_nexthop']  # bgp_nexthop ?
    assert jsontools.compare_messages_to_json_file(messages, testParams.results_output_files[0], ignore_fields)

# Underscore prevents the test from being run by pytest
# For troubleshooting: sets up kafka infra and pmacct
def t_est_start_pmacct(check_root_dir, kafka_infra_setup, prepare_test, prepare_config_local, prepare_pcap, pmacct_setup):
    assert True

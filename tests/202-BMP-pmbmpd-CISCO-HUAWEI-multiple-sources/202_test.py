
from library.py.configuration_file import KConfigurationFile
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.json_tools as jsontools
import library.py.helpers as helpers
import os, logging, pytest, sys, json, time
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], pmacct_config_filename='pmbmpd-00.conf')
confFile = KConfigurationFile(testParams.test_conf_file)

def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, pmacct_setup_teardown, prepare_pcap, consumer_setup_teardown):
    main(consumer_setup_teardown)

def main(consumer):
    for i in range(len(testParams.results_pcap_folders)):
        assert scripts.replay_pcap_with_detached_docker(testParams.results_pcap_folders[i], i, '172.111.1.' + str(100+i+1))
    messages = consumer.get_messages(180, helpers.count_non_empty_lines(testParams.output_files[0])) # 280 lines
    assert messages!=None and len(messages) > 0

    logger.debug('Waiting 10 sec')
    time.sleep(10) # needed for the last regex (WARNING) to be found in the logs!

    # Replace peer_ip_src with the correct IP address
    helpers.replace_in_file(testParams.output_files[0], '192.168.100.1', '172.111.1.101')
    helpers.replace_in_file(testParams.output_files[0], '192.168.100.2', '172.111.1.102')
    helpers.replace_in_file(testParams.output_files[0], '192.168.100.3', '172.111.1.103')

    ignore_fields = ['seq', 'timestamp', 'timestamp_arrival', 'bmp_router_port',
                     'bgp_nexthop']  # bgp_nexthop is wrong (?)
    assert jsontools.compare_messages_to_json_file(messages, testParams.output_files[0], ignore_fields)

    # Make sure the expected logs exist in pmacct log
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, testParams.log_files[0])
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING'])

    for i in range(len(testParams.results_pcap_folders)):
        scripts.stop_and_remove_traffic_container(i)

    # Make sure the expected logs exist in pmacct log
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, testParams.log_files[1])
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING(?!.*Unable to get kafka_host)'])


def t_est_start_pmacct(check_root_dir, prepare_test, prepare_config_local, prepare_pcap, pmacct_setup):
    assert True
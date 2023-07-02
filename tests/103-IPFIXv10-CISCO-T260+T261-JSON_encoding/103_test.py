
from library.py.configuration_file import KConfigurationFile
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.json_tools as jsontools
import library.py.helpers as helpers
import os, logging, pytest, sys, json, time
logger = logging.getLogger(__name__)

# The below two variables are used by setup_tools.prepare_test_env
testModuleParams = KModuleParams(sys.modules[__name__])
confFile = KConfigurationFile(testModuleParams.test_conf_file)

# Fixtures explained
# check_root_dir: makes sure pytest is run from the top level directory of the framework
# kafka_infra_setup_teardown: setup (and teardown) of kafka infrastructure
# prepare_test: creates results folder, pmacct_mount, etc. and copies all needed files there
#               edits pmacct config file with framework-specific details (IPs, ports, paths, etc.)
# prepare_pcap: edits pcap configuration file with framework-specific IPs and hostnames
# pmacct_setup_teardown: setup (and teardown) of pmacct container itself
def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, pmacct_setup_teardown, prepare_pcap, consumerJson_setup_teardown):
    consumer = consumerJson_setup_teardown
    pcap_config_files, output_files, _ = prepare_pcap
    assert len(pcap_config_files)>0 and len(output_files)>0

    assert scripts.replay_pcap_with_docker(testModuleParams.results_pcap_folders[0], '172.111.1.101')
    messages = consumer.get_messages(120, helpers.count_non_empty_lines(output_files[0])) # 12 lines
    assert messages != None and len(messages) > 0

    # Check for ERRORs or WARNINGs
    assert not helpers.check_regex_sequence_in_file(testModuleParams.results_log_file, ['ERROR|WARNING'])

    # Replace peer_ip_src with the correct IP address
    helpers.replace_in_file(output_files[0], '192.168.100.1', '172.111.1.101')

    ignore_fields = ['timestamp_max', 'timestamp_arrival', 'stamp_inserted', 'timestamp_min', 'stamp_updated']
    assert jsontools.compare_messages_to_json_file(messages, output_files[0], ignore_fields)

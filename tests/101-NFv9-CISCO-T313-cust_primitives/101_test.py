
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
def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, pmacct_setup_teardown, prepare_pcap, consumer_setup_teardown):
    consumer = consumer_setup_teardown
    pcap_config_files, output_files, log_files = prepare_pcap
    assert len(pcap_config_files)>0 and len(output_files)>0 and len(log_files) > 0

    assert scripts.replay_pcap_with_docker(testModuleParams.results_pcap_folders[0], '172.111.1.101')
    logger.info('Pcap file replayed successfully')
    messages = consumer.get_messages(120, helpers.count_non_empty_lines(output_files[0])) # 51 lines
    assert messages != None and len(messages) > 0

    logger.info('Waiting 15 seconds')
    time.sleep(15)  # needed for the last message ('Purging cache - END (PID: xx, QN: 51/51, ET: 0)') to exist in logs

    # Check for ERRORs or WARNINGs
    assert not helpers.check_regex_sequence_in_file(testModuleParams.results_log_file, ['ERROR|WARNING'])

    with open(output_files[0]) as f:
        lines = f.readlines()
    jsons = [json.dumps(msg.value()) for msg in messages]
    ignore_fields = ['peer_ip_src', 'timestamp_start', 'timestamp_end', 'timestamp_arrival', 'timestamp_min', \
                     'timestamp_max', 'stamp_inserted', 'stamp_updated']
    assert jsontools.compare_json_lists(jsons, lines, ignore_fields)

    # Make sure the expected logs exist in pmacct log
    assert helpers.check_file_regex_sequence_in_file(testModuleParams.results_log_file, log_files[0])

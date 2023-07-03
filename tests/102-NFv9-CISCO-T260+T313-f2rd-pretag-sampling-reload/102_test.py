
from library.py.configuration_file import KConfigurationFile
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.json_tools as jsontools
import library.py.helpers as helpers
import shutil, logging, pytest, sys, json, time
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__])
confFile = KConfigurationFile(testParams.test_conf_file)

def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, pmacct_setup_teardown, prepare_pcap, consumer_setup_teardown):
    main(consumer_setup_teardown)

def main(consumer):
    helpers.replace_in_file(testParams.log_files[0], '/etc/pmacct', testParams.pmacct_mount_folder, 'Reading configuration file')
    helpers.replace_in_file(testParams.log_files[1], '/etc/pmacct', testParams.pmacct_mount_folder)

    # Replaying traffic from folder pcap_mount_0 (traffic.pcap, traffic-reproducer.conf)
    assert scripts.replay_pcap_with_docker(testParams.results_pcap_folders[0], '172.111.1.101')
    messages = consumer.get_messages(120, helpers.count_non_empty_lines(testParams.output_files[0])) # 35 lines
    assert messages != None and len(messages) > 0
    logger.info('Waiting 10 seconds')
    time.sleep(10)  # needed for the last message to exist in logs

    # Replace peer_ip_src with the correct IP address in files output-flow-00.json and output-flow-01.json
    helpers.replace_in_file(testParams.output_files[0], '192.168.100.1', '172.111.1.101')
    helpers.replace_in_file(testParams.output_files[1], '192.168.100.1', '172.111.1.101')

    # Compare received json messages with output-flow-00.json
    ignore_fields = ['timestamp_start', 'timestamp_end', 'timestamp_arrival', 'timestamp_min',
                     'timestamp_max', 'stamp_inserted', 'stamp_updated']
    assert jsontools.compare_messages_to_json_file(messages, testParams.output_files[0], ignore_fields)

    # Make sure the expected logs (in output-log-00.log) exist in pmacct log
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, testParams.log_files[0])
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING'])

    # Replace -00 maps with -01 maps
    for filename in [testParams.results_mount_folder + '/' + mf for mf in ['f2rd', 'pretag', 'sampling']]:
        shutil.copyfile(filename + '-00.map', filename + '-00.map.bak')
        shutil.move(filename + '-01.map', filename + '-00.map')

    # Sending the signal to reload maps
    assert scripts.send_signal_to_pmacct('SIGUSR2')

    # Replaying traffic from folder pcap_mount_0 (traffic.pcap, traffic-reproducer.conf)
    assert scripts.replay_pcap_with_docker(testParams.results_pcap_folders[0], '172.111.1.101')
    messages = consumer.get_messages(120, helpers.count_non_empty_lines(testParams.output_files[1]))  # 35 lines
    assert messages != None and len(messages) > 0
    logger.info('Waiting 10 seconds')
    time.sleep(10)  # needed for the last message to exist in logs

    # Comparing received json messages to output-flow-01.json
    assert jsontools.compare_messages_to_json_file(messages, testParams.output_files[1], ignore_fields)

    # Make sure the expected logs (in output-log-01.log) exist in pmacct log
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, testParams.log_files[1])
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING'])

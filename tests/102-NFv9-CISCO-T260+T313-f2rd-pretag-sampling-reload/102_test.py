
from library.py.configuration_file import KConfigurationFile
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import shutil, logging, pytest, sys, time
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__])
confFile = KConfigurationFile(testParams.test_conf_file)

def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, pmacct_setup_teardown, prepare_pcap, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def main(consumer):
    assert scripts.replay_pcap_with_docker(testParams.pcap_folders[0], '172.111.1.101')

    assert test_tools.read_and_compare_messages(consumer, testParams.output_files.getFileLike('flow-00'),
        [('192.168.100.1', '172.111.1.101')],
        ['timestamp_start', 'timestamp_end', 'timestamp_arrival',
         'timestamp_min', 'timestamp_max', 'stamp_inserted', 'stamp_updated'])

    # Make sure the expected logs (in output-log-00.log) exist in pmacct log
    helpers.replace_in_file(testParams.log_files[0], '/etc/pmacct', testParams.pmacct_mount_folder, 'Reading configuration file')
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, testParams.log_files[0])
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING'])

    # Replace -00 maps with -01 maps
    for filename in [testParams.results_mount_folder + '/' + mf for mf in ['f2rd', 'pretag', 'sampling']]:
        shutil.copyfile(filename + '-00.map', filename + '-00.map.bak')
        shutil.move(filename + '-01.map', filename + '-00.map')

    # Sending the signal to reload maps
    assert scripts.send_signal_to_pmacct('SIGUSR2')

    assert scripts.replay_pcap_with_docker(testParams.pcap_folders[0], '172.111.1.101')

    assert test_tools.read_and_compare_messages(consumer, testParams.output_files.getFileLike('flow-01'),
        [('192.168.100.1', '172.111.1.101')],
        ['timestamp_start', 'timestamp_end', 'timestamp_arrival',
         'timestamp_min', 'timestamp_max', 'stamp_inserted', 'stamp_updated'])

    helpers.replace_in_file(testParams.log_files[1], '/etc/pmacct', testParams.pmacct_mount_folder)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, testParams.log_files[1])
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING'])

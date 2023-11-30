
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import shutil, logging, pytest, sys
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], ipv4_subnet='192.168.100.')

@pytest.mark.ipfix
@pytest.mark.ipfix_only
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def transform_log_file(logfile):
    helpers.replace_in_file(logfile, '/etc/pmacct', testParams.pmacct_mount_folder, 'Reading configuration file')
    helpers.replace_in_file(logfile, '.map]', '-00.map]')
    helpers.replace_in_file(logfile, 'primitives.lst', 'primitives-00.lst')
    test_tools.transform_log_file(logfile)

def main(consumer):
    assert scripts.replay_pcap(testParams.pcap_folders[0])

    assert test_tools.read_and_compare_messages(consumer, testParams, 'flow-00',
        ['timestamp_arrival', 'timestamp_min', 'timestamp_max', 'stamp_inserted', 'stamp_updated'])

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-00')
    transform_log_file(logfile)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN'])

    # Replace -00 maps with -01 maps
    for filename in [testParams.results_mount_folder + '/' + mf for mf in ['f2rd', 'pretag', 'sampling']]:
        shutil.copyfile(filename + '-00.map', filename + '-00.map.bak')
        shutil.move(filename + '-01.map', filename + '-00.map')

    # Sending the signal to reload maps
    assert scripts.send_signal_to_pmacct('SIGUSR2')

    assert scripts.replay_pcap(testParams.pcap_folders[0])

    assert test_tools.read_and_compare_messages(consumer, testParams, 'flow-01',
        ['timestamp_arrival', 'timestamp_min', 'timestamp_max', 'stamp_inserted', 'stamp_updated'])

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-01')
    transform_log_file(logfile)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN'])

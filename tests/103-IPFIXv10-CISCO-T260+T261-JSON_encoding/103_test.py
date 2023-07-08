
from library.py.configuration_file import KConfigurationFile
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.helpers as helpers
import logging, pytest, sys, time
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__])
confFile = KConfigurationFile(testParams.test_conf_file)

def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, pmacct_setup_teardown, prepare_pcap, consumerJson_setup_teardown):
    main(consumerJson_setup_teardown[0]) # Plain Json consumer used here

def main(consumer):
    assert scripts.replay_pcap_with_docker(testParams.pcap_folders[0], '172.111.1.101')

    assert test_tools.read_and_compare_messages(consumer, testParams.output_files.getFileLike('flow-00'),
        [('192.168.100.1', '172.111.1.101')],
        ['timestamp_start', 'timestamp_end', 'timestamp_arrival', 'timestamp_min', 'timestamp_max',
         'stamp_inserted', 'stamp_updated'])

    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING'])

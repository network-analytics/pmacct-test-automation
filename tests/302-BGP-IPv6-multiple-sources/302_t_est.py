
import shutil
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import logging, pytest, sys, time, datetime, os
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], ipv4_subnet='192.168.100.', ipv6_subnet='cafe::')
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def prep_pcap():
    os.makedirs(testParams.results_folder + '/pcap_mount')
    shutil.copytree(testParams.pcap_folders[2], testParams.results_folder + '/pcap_mount/pcap1')
    shutil.copytree(testParams.pcap_folders[3], testParams.results_folder + '/pcap_mount/pcap2')

def main(consumer):
    prep_pcap()
    pass
    return

    while datetime.datetime.now().second < 35:
        time.sleep(1)
        pass

    assert scripts.replay_pcap_with_detached_docker(testParams.pcap_folders[0], 0, '172.111.1.101', 'fd25::101')
    assert scripts.replay_pcap_with_detached_docker(testParams.pcap_folders[1], 1, '172.111.1.103')
    assert scripts.replay_pcap_with_detached_docker_dual(testParams.pcap_folders[2], testParams.pcap_folders[3], 2,
                                                         '172.111.1.102')

    assert test_tools.read_and_compare_messages(consumer, testParams.output_files.getFileLike('bgp-00'),
        [('192.168.100.3', '172.111.1.103'), ('192.168.100.2', '172.111.1.102'), ('cafe::1', 'fd25::101')],
        ['timestamp_start', 'timestamp_end', 'timestamp_max', 'timestamp_arrival', 'stamp_inserted',
                                                 'timestamp_min', 'stamp_updated'])

    #assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING'])

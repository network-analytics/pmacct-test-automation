
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.test_tools as test_tools
import logging, pytest, sys
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__])

def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def main(consumer):
    assert scripts.replay_pcap(testParams.pcap_folders[0])

    assert test_tools.read_and_compare_messages(consumer, testParams.output_files.getFileLike('flow-00'),
        [('192.168.100.1', '172.111.1.101')],
        ['stamp_inserted', 'stamp_updated', 'timestamp_max', 'timestamp_arrival', 'timestamp_min'])

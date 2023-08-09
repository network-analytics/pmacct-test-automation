
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.test_tools as test_tools
import library.py.helpers as helpers
import logging, pytest, sys, time
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], ipv4_subnet='192.168.100.')

def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def main(consumer):
    logger.debug('Waiting 10 sec')
    time.sleep(10)

    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-00')
    test_tools.transform_log_file(logfile)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING'])

    #consumer.get_messages(120, 1)
    consumer.disconnect() # For the Kafka consumer not to hang when Kafka is killed
    scripts.stop_and_remove_kafka_containers()

    assert scripts.replay_pcap(testParams.pcap_folders[0])

    logger.debug('Waiting 90 seconds for pmacct to attempt sending to Kafka')
    time.sleep(90)

    logfile = testParams.log_files.getFileLike('log-01')
    test_tools.transform_log_file(logfile)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)

    scripts.stop_and_remove_traffic_container(0)

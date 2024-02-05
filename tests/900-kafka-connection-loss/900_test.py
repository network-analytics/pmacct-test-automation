
from library.py.test_params import KModuleParams
import library.py.scripts as scripts
import library.py.test_tools as test_tools
import library.py.helpers as helpers
import logging, pytest
logger = logging.getLogger(__name__)

testParams = KModuleParams(__file__, daemon='nfacctd', ipv4_subnet='192.168.100.')

@pytest.mark.signals
@pytest.mark.nfacctd
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def main(consumer):
    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-00')
    test_tools.transform_log_file(logfile)
    assert helpers.retry_until_true('Checking expected logs',
        lambda: helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile), 30, 5)
    #assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN'])

    consumer.disconnect() # For the Kafka consumer not to hang when Kafka is killed
    # Kafka infrastructure is stopped
    scripts.stop_and_remove_kafka_containers()

    assert scripts.replay_pcap(testParams.pcap_folders[0])

    logfile = testParams.log_files.getFileLike('log-01')
    test_tools.transform_log_file(logfile)
    assert helpers.retry_until_true('Checking expected logs',
        lambda: helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile), 90, 10)

    scripts.stop_and_remove_traffic_container(testParams.pcap_folders[0])

    # We want to leave the Kafka infrastructure running, for the next test case to use, so we re-deploy it
    assert scripts.start_kafka_containers()
    assert scripts.wait_schemaregistry_healthy(120)

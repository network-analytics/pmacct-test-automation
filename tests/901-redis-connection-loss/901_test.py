
from library.py.setup_tools import KModuleParams
import library.py.scripts as scripts
import library.py.test_tools as test_tools
import library.py.helpers as helpers
import logging, pytest, sys, time
logger = logging.getLogger(__name__)

testParams = KModuleParams(sys.modules[__name__], ipv4_subnet='192.168.100.')

# added redis fixture below, that's why the test_core fixture is not used here
def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, redis_setup_teardown, pmacct_setup_teardown,
         prepare_pcap, consumer_setup_teardown):
    main(consumer_setup_teardown[0])

def transform_log_file(logfile):
    helpers.replace_in_file(logfile, '${redis_ip}', '172.111.1.14')
    helpers.replace_in_file(logfile, '${redis_port}', '6379')
    test_tools.transform_log_file(logfile)

def main(consumer):
    # Make sure the expected logs exist in pmacct log
    logfile = testParams.log_files.getFileLike('log-00')
    transform_log_file(logfile)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARNING'])

    scripts.stop_and_remove_redis_container()

    logfile = testParams.log_files.getFileLike('log-01')
    test_tools.transform_log_file(logfile)
    assert helpers.retry_until_true('Checking expected logs',
        lambda: helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile), 30, 10)

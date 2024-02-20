
from library.py.test_params import KModuleParams
import library.py.helpers as helpers
import logging
import pytest
import library.py.test_tools as test_tools
logger = logging.getLogger(__name__)

testParams = KModuleParams(__file__, daemon='nfacctd', ipv4_subnet='192.168.100.')


@pytest.mark.nfacctd
@pytest.mark.bmp
@pytest.mark.bmp_only
@pytest.mark.bmpv3
def test(test_core, consumer_setup_teardown):
    main(consumer_setup_teardown)


def main(consumers):
    th = test_tools.KTestHelper(testParams, consumers)
    assert th.spawn_traffic_container('traffic-reproducer-200')

    th.set_ignored_fields(['seq', 'timestamp', 'timestamp_arrival', 'bmp_router_port'])
    assert th.read_and_compare_messages('daisy.bmp', 'bmp-00')

    logfile = testParams.log_files.getFileLike('log-00')
    helpers.replace_in_file(logfile, '/etc/pmacct/librdkafka.conf', testParams.pmacct_mount_folder + '/librdkafka.conf')
    th.transform_log_file('log-00', 'traffic-reproducer-200')
    assert th.wait_and_check_logs('log-00', 30, 10)

    assert not th.check_regex_in_pmacct_log('ERROR|WARN(?!.*Unable to get kafka_host)')

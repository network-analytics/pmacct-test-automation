###################################################
# Automated Testing Framework for Network Analytics
#
# functions for preparing the environment for the
# test case to run in
#
###################################################

import library.py.scripts as scripts
import shutil, secrets
from library.py.helpers import *
from library.py.configuration_file import KConfigurationFile
logger = logging.getLogger(__name__)


class KModuleParams:
    def __init__(self, _module, pmacct_config_filename=''):
        self.pmacct_config_filename = pmacct_config_filename
        self.build_static_params(_module.__file__)

    def build_static_params(self, filename: str):
        self.test_folder = os.path.dirname(filename)
        self.tests_folder = os.path.dirname(self.test_folder)
        self.root_folder = os.path.dirname(self.tests_folder)
        self.test_name = os.path.basename(self.test_folder)
        self.test_mount_folder = self.test_folder + '/pmacct_mount'
        self.pmacct_mount_folder = '/var/log/pmacct'
        self.pmacct_output_folder = self.pmacct_mount_folder + '/pmacct_output'
        if self.pmacct_config_filename!='':
            self.test_conf_file = self.test_folder + '/' + self.pmacct_config_filename
        else:
            self.test_conf_file = self.test_folder + '/pmacctd.conf'
            if not os.path.isfile(self.test_conf_file):
                fnames = select_files(self.test_folder, 'nfacctd.+conf$')
                assert len(fnames)==1
                self.test_conf_file = self.test_folder + '/' + fnames[0]
        self.results_folder = os.getcwd() + '/results/' + self.test_name
        self.results_conf_file = self.results_folder + '/pmacctd.conf'
        self.results_mount_folder = self.results_folder + '/pmacct_mount'
        self.results_pcap_folders = []
        self.results_output_folder = self.results_mount_folder + '/pmacct_output'
        self.kafka_topic_name = 'test.topic.' + secrets.token_hex(4)[:8]
        self.pmacct_log_file = self.results_output_folder + '/pmacctd.log'
        self.results_msg_dump = self.results_folder + '/message_dump.json'
        self.output_files = []
        self.log_files = []


def create_mount_and_output_folders(params: KModuleParams):
    logger.info('Creating test mount folder: ' + short_name(params.results_mount_folder))
    os.makedirs(params.results_mount_folder)
    logger.info('Creating test output folder: ' + short_name(params.results_output_folder))
    _mask = os.umask(0)
    os.makedirs(params.results_output_folder, 0o777)
    os.umask(_mask)
    logger.debug('Mount and output folders created')

# Files in mounted folder, for pmacct to read
def edit_conf_mount_folder(config: KConfigurationFile, params: KModuleParams):
    config.replace_value_of_key('kafka_config_file', params.pmacct_mount_folder + '/librdkafka.conf')
    config.replace_value_of_key('pre_tag_map', params.pmacct_mount_folder + '/pretag-00.map')
    config.replace_value_of_key('flow_to_rd_map', params.pmacct_mount_folder + '/f2rd-00.map')
    config.replace_value_of_key('sampling_map', params.pmacct_mount_folder + '/sampling-00.map')
    config.replace_value_of_key('aggregate_primitives', params.pmacct_mount_folder + '/custom-primitives-00.lst')

# Files in output folder, for pmacct to write
def edit_conf_output_folder(config: KConfigurationFile, params: KModuleParams):
    config.replace_value_of_key('logfile', params.pmacct_output_folder + '/pmacctd.log')
    config.replace_value_of_key('pidfile', params.pmacct_output_folder + '/pmacctd.pid')
    config.replace_value_of_key('avro_schema_output_file', params.pmacct_output_folder + '/flow_avroschema.avsc')

# Replace specific operational values
def edit_conf_operational(config: KConfigurationFile, params: KModuleParams):
    config.replace_value_of_key('kafka_topic', params.kafka_topic_name)
    config.replace_value_of_key('kafka_avro_schema_registry', 'http://schema-registry:8081')
    config.replace_value_of_key('debug', 'true')

# Replace specific BMP values
def edit_conf_bmp(config: KConfigurationFile, params: KModuleParams):
    config.replace_value_of_key('bmp_daemon_tag_map', params.pmacct_mount_folder + '/pretag-00.map')
    config.replace_value_of_key('bmp_daemon_msglog_kafka_topic', params.kafka_topic_name)
    config.replace_value_of_key('bmp_daemon_msglog_kafka_config_file', '/var/log/pmacct/librdkafka.conf')
    config.replace_value_of_key('bmp_daemon_msglog_kafka_avro_schema_registry', 'http://schema-registry:8081')
    config.replace_value_of_key('bmp_daemon_msglog_avro_schema_output_file', params.pmacct_output_folder)

# Replace specific BGP values
def edit_conf_bgp(config: KConfigurationFile, params: KModuleParams):
    config.replace_value_of_key('bgp_daemon_tag_map', params.pmacct_mount_folder + '/pretag-00.map')
    config.replace_value_of_key('bgp_daemon_msglog_kafka_topic', params.kafka_topic_name)
    config.replace_value_of_key('bgp_daemon_msglog_kafka_config_file', '/var/log/pmacct/librdkafka.conf')
    config.replace_value_of_key('bgp_daemon_msglog_kafka_avro_schema_registry', 'http://schema-registry:8081')
    config.replace_value_of_key('bgp_daemon_msglog_avro_schema_output_file', params.pmacct_output_folder)

# Copy existing files in pmacct_mount to result (=actual) mounted folder
def copy_files_in_mount_folder(params: KModuleParams):
    if os.path.exists(params.test_mount_folder):
        src_files = os.listdir(params.test_mount_folder)
        count = 0
        for file_name in src_files:
            full_file_name = os.path.join(params.test_mount_folder, file_name)
            if os.path.isfile(full_file_name) and not file_name.startswith('.'):
                count += 1
                logger.debug('Copying: ' + short_name(full_file_name))
                shutil.copy(full_file_name, params.results_mount_folder)
        logger.info('Copied ' + str(count) + ' files')


def replace_IPs(filename: str):
    if file_contains_string(filename, '192.168.100.1'):
        replace_in_file(filename, '192.168.100.1', '172.111.1.101')
    if file_contains_string(filename, '192.168.100.2'):
        replace_in_file(filename, '192.168.100.2', '172.111.1.102')
    if file_contains_string(filename, '192.168.100.3'):
        replace_in_file(filename, '192.168.100.3', '172.111.1.103')
    if file_contains_string(filename, 'cafe::1'):
        replace_in_file(filename, 'cafe::1', 'fd25::101')
    if file_contains_string(filename, 'cafe::2'):
        replace_in_file(filename, 'cafe::2', 'fd25::102')
    if file_contains_string(filename, 'cafe::3'):
        replace_in_file(filename, 'cafe::3', 'fd25::103')


# RUNS BEFORE PMACCT IS RUN
# Prepares results folder to receive logs and output from pmacct
def prepare_test_env(_module):
    params = _module.testParams
    config = _module.confFile

    logger.info('Test name: ' + params.test_name)

    if os.path.exists(params.results_folder):
        logger.debug('Results folder exists, deleting folder ' + short_name(params.results_folder))
        shutil.rmtree(params.results_folder)
        assert not os.path.exists(params.results_folder)
    create_mount_and_output_folders(params)

    edit_conf_mount_folder(config, params)
    edit_conf_output_folder(config, params)
    edit_conf_operational(config, params)
    edit_conf_bmp(config, params)
    edit_conf_bgp(config, params)

    # Output to new conf file in mount folder
    config.print_to_file(params.results_conf_file)

    copy_files_in_mount_folder(params)

    results_pretag_files = select_files(params.results_mount_folder, '.+\\.map$')
    for results_pretag_file in results_pretag_files:
        replace_IPs(params.results_mount_folder + '/' + results_pretag_file)

    shutil.copy(params.root_folder + '/library/librdkafka.conf', params.results_mount_folder)


# RUNS AFTER PMACCT IS RUN
# Prepares json output, log, pcap and pcap-config files
def prepare_pcap(_module):
    params = _module.testParams
    test_config_files = select_files(params.test_folder, 'traffic-reproducer.*-\\d+.conf$')
    test_pcap_files = select_files(params.test_folder, 'traffic.*-\\d+.pcap$')
    test_output_files = select_files(params.test_folder, 'output.*-\\d+.json$')
    test_log_files = select_files(params.test_folder, 'output.*-\\d+.log$')

    assert len(test_pcap_files)>0
    assert len(test_pcap_files)==len(test_config_files)
    assert len(test_output_files)>0

    def copyList(filelist):
        retVal = []
        for filename in filelist:
            retVal.append(params.results_folder + '/' + filename)
            shutil.copy(params.test_folder + '/' + filename, params.results_folder + '/' + filename)
        return retVal

    params.output_files = copyList(test_output_files)
    params.log_files = copyList(test_log_files)

    for i in range(len(test_config_files)):
        results_pcap_folder = params.results_folder + '/pcap_mount_' + str(i)
        os.makedirs(results_pcap_folder)
        logger.debug('Created folder ' + short_name(results_pcap_folder))
        params.results_pcap_folders.append(results_pcap_folder)
        shutil.copy(params.test_folder + '/' + test_config_files[i], results_pcap_folder + '/traffic-reproducer.conf')
        shutil.copy(params.test_folder + '/' + test_pcap_files[i], results_pcap_folder + '/traffic.pcap')
        confPcap = KConfigurationFile(results_pcap_folder + '/traffic-reproducer.conf')
        confPcap.replace_value_of_key('pcap', '/pcap/traffic.pcap')
        if confPcap.uses_ipv6():
            logger.debug('Traffic uses IPv6')
            confPcap.replace_value_of_key('    ip', 'fd25::13')
        else:
            logger.debug('Traffic uses IPv4')
            confPcap.replace_value_of_key('    ip', '172.111.1.13')
        confPcap.print_to_file(results_pcap_folder + '/traffic-reproducer.conf')
        replace_IPs(results_pcap_folder + '/traffic-reproducer.conf')






    # following didn't work (possibly because the order is changed when dumped back?)
    # import yaml
    # with open(pcap_config_file) as f:
    #     data = yaml.load(f, Loader=yaml.FullLoader)
    # data['network']['map'][0]['repro_ip'] = '127.0.0.1'
    # data['bmp']['collector']['ip'] = '127.0.0.1'
    # data['bmp']['collector']['port'] = '2929'
    # with open(pcap_config_file, 'w') as f:
    #     data = yaml.dump(data, f)


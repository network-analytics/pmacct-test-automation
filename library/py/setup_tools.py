###################################################
# Automated Testing Framework for Network Analytics
# Functions for preparing the environment for the
# test case to run in
# nikolaos.tsokas@swisscom.com 11/05/2023
###################################################

import shutil, secrets, yaml
from library.py.helpers import *
from library.py.configuration_file import KConfigurationFile
logger = logging.getLogger(__name__)


class KModuleParams:
    def __init__(self, _module, daemon='nfacctd', ipv4_subnet='', ipv6_subnet=''):
        self.daemon = daemon
        self.test_subnet_ipv4 = ipv4_subnet
        self.test_subnet_ipv6 = ipv6_subnet
        self.build_static_params(_module.__file__)

    def build_static_params(self, filename: str):
        self.test_folder = os.path.dirname(filename)
        self.tests_folder = os.path.dirname(self.test_folder)
        self.root_folder = os.path.dirname(self.tests_folder)
        self.test_name = os.path.basename(self.test_folder)
        self.test_mount_folder = self.test_folder + '/pmacct_mount'
        self.pmacct_mount_folder = '/var/log/pmacct'
        self.pmacct_output_folder = self.pmacct_mount_folder + '/pmacct_output'
        self.test_conf_file = '' # self.test_folder + '/' + self.daemon + '-00.conf'
        self.results_folder = os.getcwd() + '/results/' + self.test_name
        self.monitor_file = self.root_folder + '/results/monitor.log'
        self.results_conf_file = self.results_folder + '/' + self.daemon + '.conf'
        self.results_mount_folder = self.results_folder + '/pmacct_mount'
        self.pcap_folders = self.output_files = self.log_files = []
        self.test_output_files = self.test_log_files = []
        self.results_output_folder = self.results_mount_folder + '/pmacct_output'
        self.kafka_topics = {}
        self.pmacct_log_file = self.results_output_folder + '/pmacctd.log'

    def build_dynamic_params(self, scenario):
        if scenario=='default':
            self.test_conf_file = self.test_folder + '/' + self.daemon + '-00.conf'
            self.test_output_files = select_files(self.test_folder, 'output.*-\\d+.json$')
            self.test_log_files = select_files(self.test_folder, 'output.*-\\d+.txt$')
        else:
            self.test_conf_file = self.test_folder + '/' + scenario + '/' + self.daemon + '-00.conf'
            self.test_output_files = select_files(self.test_folder + '/' + scenario, 'output.*-\\d+.json$')
            self.test_log_files = select_files(self.test_folder + '/' + scenario, 'output.*-\\d+.txt$')
        logger.debug('Test config file: ' + self.test_conf_file)
        logger.debug('Test output files: ' + str(self.test_output_files))
        logger.debug('Test log files: ' + str(self.test_log_files))

    def replace_IPs(self, filename: str):
        if self.test_subnet_ipv4!='' and file_contains_string(filename, self.test_subnet_ipv4):
            replace_in_file(filename, self.test_subnet_ipv4, '172.21.1.10')
        if self.test_subnet_ipv6!='' and file_contains_string(filename, self.test_subnet_ipv6):
            replace_in_file(filename, self.test_subnet_ipv6, 'fd25::10')

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
    config.replace_value_of_key('flow_to_rd_map', params.pmacct_mount_folder + '/f2rd-00.map')
    config.replace_value_of_key('sampling_map', params.pmacct_mount_folder + '/sampling-00.map')
    config.replace_value_of_key('aggregate_primitives', params.pmacct_mount_folder + '/custom-primitives-00.lst')

# Files in output folder, for pmacct to write
def edit_conf_output_folder(config: KConfigurationFile, params: KModuleParams):
    config.replace_value_of_key('logfile', params.pmacct_output_folder + '/pmacctd.log')
    config.replace_value_of_key('pidfile', params.pmacct_output_folder + '/pmacctd.pid')

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


# RUNS BEFORE PMACCT IS RUN
# Prepares results folder to receive logs and output from pmacct
def prepare_test_env(_module, scenario):
    params = _module.testParams
    params.build_dynamic_params(scenario) # selects the right files from test folder, as per scenario
    config = KConfigurationFile(_module.testParams.test_conf_file)

    topicsDict = config.get_kafka_topics()
    for k in topicsDict.keys():
        params.kafka_topics[k] = topicsDict[k] + '.' + secrets.token_hex(4)[:8]
        config.replace_value_of_key(k, params.kafka_topics[k])
    logger.debug('Kafka topic(s): ' + str(params.kafka_topics))

    if os.path.exists(params.results_folder):
        logger.debug('Results folder exists, deleting folder ' + short_name(params.results_folder))
        shutil.rmtree(params.results_folder)
        assert not os.path.exists(params.results_folder)
    create_mount_and_output_folders(params)

    edit_conf_mount_folder(config, params)
    edit_conf_output_folder(config, params)
    config.replace_value_of_key('bgp_neighbors_file', params.pmacct_output_folder + '/nfacctd_bgp_neighbors.lst')
    config.replace_value_of_key_ending_with('avro_schema_file', params.pmacct_output_folder + '/avsc/nfacctd_msglog_avroschema.avsc')
    config.replace_value_of_key_ending_with('avro_schema_output_file', params.pmacct_output_folder + '/avsc/nfacctd_msglog_avroschema.avsc')
    config.replace_value_of_key_ending_with('_tag_map', params.pmacct_mount_folder + '/pretag-00.map')
    config.replace_value_of_key_ending_with('kafka_config_file', params.pmacct_mount_folder + '/librdkafka.conf')
    config.replace_value_of_key_ending_with('kafka_avro_schema_registry', 'http://schema-registry:8081')
    config.replace_value_of_key('redis_host', '172.21.1.14:6379')

    # Output to new conf file in mount folder
    config.print_to_file(params.results_conf_file)

    copy_files_in_mount_folder(params)

    results_pretag_files = select_files(params.results_mount_folder, '.+\\.map$')
    for results_pretag_file in results_pretag_files:
        params.replace_IPs(params.results_mount_folder + '/' + results_pretag_file)

    shutil.copy(params.root_folder + '/library/librdkafka.conf', params.results_mount_folder)

    def copyList(filelist):
        retVal = KFileList()
        for filename in filelist:
            retVal.append(params.results_folder + '/' + filename)
            scenarioFolder = '' if scenario=='default' else scenario + '/'
            shutil.copy(params.test_folder + '/' + scenarioFolder + filename, params.results_folder + '/' + filename)
        return retVal
    params.output_files = copyList(params.test_output_files)
    params.log_files = copyList(params.test_log_files)


class KFileList(list):

    def getFileLike(self, txt):
        for filename in self:
            basename = os.path.basename(filename)
            if txt in basename:
                return filename
        return None

def fix_repro_ip_in_config(ip_subnet, config, fw_ip):
    if len(ip_subnet) < 1:
        logger.info('Reference subnet not set, assuming traffic reproduction IP from framework subnet')
    else:
        logger.info('Reference subnet set, setting traffic reproduction IP to framework subnet')
        config['network']['map'][0]['repro_ip'] = config['network']['map'][0]['repro_ip']. \
            replace(ip_subnet, fw_ip)

# RUNS AFTER PMACCT IS RUN
# Prepares json output, log, pcap and pcap-config files
def prepare_pcap(_module):
    params = _module.testParams
    test_config_files = select_files(params.test_folder, 'traffic-reproducer.*-\\d+.yml$')
    test_pcap_files = select_files(params.test_folder, 'traffic.*-\\d+.pcap$')
    assert len(test_pcap_files)==len(test_config_files)

    for i in range(len(test_config_files)):
        results_pcap_folder = params.results_folder + '/pcap_mount_' + str(i)
        os.makedirs(results_pcap_folder)
        logger.debug('Created folder ' + short_name(results_pcap_folder))
        params.pcap_folders.append(results_pcap_folder)
        shutil.copy(params.test_folder + '/' + test_config_files[i], results_pcap_folder + '/traffic-reproducer.yml')
        shutil.copy(params.test_folder + '/' + test_pcap_files[i], results_pcap_folder + '/traffic.pcap')

        with open(results_pcap_folder + '/traffic-reproducer.yml') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        data['pcap'] = '/pcap/traffic.pcap'

        # adding pmacct IP address
        isIPv6 = ':' in data['network']['map'][0]['repro_ip']
        pmacct_ip = 'fd25::13' if isIPv6 else '172.21.1.13'
        logger.debug('Traffic uses ' + ('IPv6' if isIPv6 else 'IPv4'))
        for k in ['bmp', 'bgp', 'ipfix']:
            if k in data:
                data[k]['collector']['ip'] = pmacct_ip

        if isIPv6:
            fix_repro_ip_in_config(params.test_subnet_ipv6, data, 'fd25::10')
        else:
            fix_repro_ip_in_config(params.test_subnet_ipv4, data, '172.21.1.10')

        with open(results_pcap_folder + '/traffic-reproducer.yml', 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

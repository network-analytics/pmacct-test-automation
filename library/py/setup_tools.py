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

    # Static params and params for default scenario
    def build_static_params(self, filename: str):
        self.test_folder = os.path.dirname(filename)
        self.tests_folder = os.path.dirname(self.test_folder)
        self.root_folder = os.path.dirname(self.tests_folder)
        self.fw_config = read_config_file(self.root_folder + '/settings.conf')
        self.test_name = os.path.basename(self.test_folder)
        self.test_mount_folder = self.test_folder + '/pmacct_mount'
        self.pmacct_mount_folder = '/var/log/pmacct'
        self.pmacct_output_folder = self.pmacct_mount_folder + '/pmacct_output'
        self.monitor_file = self.root_folder + '/results/monitor.log'
        # by default no scenario set (may be overriden later in build_dynamic_params
        self.results_folder = os.getcwd() + '/results/' + self.test_name
        self.set_results_folders()

        self.pcap_folders = self.output_files = self.log_files = []
        self.kafka_topics = {}

        self.test_conf_file = self.test_folder + '/' + self.daemon + '-00.conf'
        self.test_output_files = select_files(self.test_folder, 'output.*-\\d+.json$')
        self.test_log_files = select_files(self.test_folder, 'output.*-\\d+.txt$')

    # Sets subfolder of test results folder. This is run once for the default scenario.
    # If it is determined that it is about a specific scenario, this function is re-executed (see function below)
    def set_results_folders(self):
        self.pmacct_docker_compose_file = self.results_folder + '/docker-compose-pmacct.yml'
        self.results_conf_file = self.results_folder + '/' + self.daemon + '.conf'
        self.results_mount_folder = self.results_folder + '/pmacct_mount'
        self.results_dump_folder = self.results_folder + '/kafka_dumps'
        self.results_output_folder = self.results_mount_folder + '/pmacct_output'
        self.pmacct_log_file = self.results_output_folder + '/pmacctd.log'

    # Dynamic params are built after it has been determined whether it is about a default
    # or about a scecific scenario
    def build_dynamic_params(self, scenario):
        self.results_folder = os.getcwd() + '/results/' + self.test_name + '__' + scenario
        self.set_results_folders()
        scenario_conf_file = self.test_folder + '/' + scenario + '/' + self.daemon + '-00.conf'
        scenario_output_files = select_files(self.test_folder + '/' + scenario, 'output.*-\\d+.json$')
        scenario_log_files = select_files(self.test_folder + '/' + scenario, 'output.*-\\d+.txt$')
        if os.path.isfile(scenario_conf_file):
            self.test_conf_file = scenario_conf_file
        if len(scenario_output_files)>0:
            self.test_output_files = scenario_output_files
        if len(scenario_log_files)>0:
            self.test_log_files = scenario_log_files
        logger.debug('Test config file: ' + self.test_conf_file)
        logger.debug('Test output files: ' + str(self.test_output_files))
        logger.debug('Test log files: ' + str(self.test_log_files))

    # Replaces IPs in file, so that they reflect the framework subnet (which may or may not be
    # different than the ones provided with the test case)
    def replace_IPs(self, filename: str):
        if self.test_subnet_ipv4!='' and file_contains_string(filename, self.test_subnet_ipv4):
            replace_in_file(filename, self.test_subnet_ipv4, '172.21.1.10')
        if self.test_subnet_ipv6!='' and file_contains_string(filename, self.test_subnet_ipv6):
            replace_in_file(filename, self.test_subnet_ipv6, 'fd25::10')

    # Creates the docker-compose file for deploying pmacct.
    def create_pmacct_compose_file(self):
        img_var_name = 'PMACCT_' + self.daemon.upper() + '_IMG'
        pmacct_img = self.fw_config.get(img_var_name)
        with open(self.root_folder + '/library/sh/pmacct_docker/docker-compose-template.yml') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        data['services']['pmacct']['image'] = pmacct_img
        vols = data['services']['pmacct']['volumes']
        for i in range(len(vols)):
            vols[i] = vols[i].replace('${PMACCT_CONF}', self.results_conf_file)
            vols[i] = vols[i].replace('${PMACCT_DAEMON}', self.daemon)
            vols[i] = vols[i].replace('${PMACCT_MOUNT}', self.results_mount_folder)
        with open(self.pmacct_docker_compose_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)


# Creates mount and output subfolders in the test results folder
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
    config.replace_value_of_key('aggregate_primitives', params.pmacct_mount_folder + '/custom-primitives-00.map')
    config.replace_value_of_key_ending_with('_tag_map', params.pmacct_mount_folder + '/pretag-00.map')
    config.replace_value_of_key_ending_with('kafka_config_file', params.pmacct_mount_folder + '/librdkafka.conf')

# Files in output folder, for pmacct to write
def edit_conf_output_folder(config: KConfigurationFile, params: KModuleParams):
    config.replace_value_of_key('logfile', params.pmacct_output_folder + '/pmacctd.log')
    config.replace_value_of_key('pidfile', params.pmacct_output_folder + '/pmacctd.pid')
    config.replace_value_of_key('bgp_neighbors_file', params.pmacct_output_folder + '/nfacctd_bgp_neighbors.lst')
    config.replace_value_of_key_ending_with('avro_schema_file',
                                            params.pmacct_output_folder + '/avsc/nfacctd_msglog_avroschema.avsc')
    config.replace_value_of_key_ending_with('avro_schema_output_file',
                                            params.pmacct_output_folder + '/avsc/nfacctd_msglog_avroschema.avsc')

# Calls above two functions; also, sets the correct schema registry URL and the correct address:port of redis
def edit_config_with_framework_params(config: KConfigurationFile, params: KModuleParams):
    edit_conf_mount_folder(config, params)
    edit_conf_output_folder(config, params)
    config.replace_value_of_key_ending_with('kafka_avro_schema_registry', 'http://schema-registry:8081')
    config.replace_value_of_key('redis_host', '172.21.1.14:6379')

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
    if scenario!='default':
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
    edit_config_with_framework_params(config, params)
    config.print_to_file(params.results_conf_file)

    copy_files_in_mount_folder(params)
    if scenario!='default': # copy scenario-specific map files to results mount folder
        for map_file in select_files(params.test_folder + '/' + scenario, '.+\\.map$'):
            shutil.copy(map_file, params.results_mount_folder)
    for results_pretag_file in select_files(params.results_mount_folder, '.+\\.map$'):
        params.replace_IPs(results_pretag_file)
    shutil.copy(params.root_folder + '/library/librdkafka.conf', params.results_mount_folder)

    def copyList(filelist):
        retVal = KFileList()
        for src_filepath in filelist:
            dst_filepath = params.results_folder + '/' + os.path.basename(src_filepath)
            retVal.append(dst_filepath)
            shutil.copy(src_filepath, dst_filepath)
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

# Fixes reproduction IP in a config object, if needed (if not, it only produces a log)
def fix_repro_ip_in_config(ip_subnet, config, fw_ip):
    if len(ip_subnet) < 1:
        logger.info('Reference subnet not set, assuming traffic reproduction IP from framework subnet')
    else:
        logger.info('Reference subnet set, setting traffic reproduction IP to framework subnet')
        config['network']['map'][0]['repro_ip'] = config['network']['map'][0]['repro_ip'].replace(ip_subnet, fw_ip)

# Creates docker-compose.yml file for a specific traffic-reproducer
def fill_repro_docker_compose(i, params, repro_ip, isIPv6):
    with open(params.root_folder + '/library/sh/traffic_docker/docker-compose-template.yml') as f:
        data_dc = yaml.load(f, Loader=yaml.FullLoader)
    data_dc['services']['traffic-reproducer']['container_name'] = 'traffic-reproducer-' + str(i)
    data_dc['services']['traffic-reproducer']['image'] = params.fw_config.get('TRAFFIC_REPRO_IMG')
    results_pcap_folder = params.results_folder + '/pcap_mount_' + str(i)
    data_dc['services']['traffic-reproducer']['volumes'][0] = results_pcap_folder + ':/pcap'
    if isIPv6:
        data_dc['services']['traffic-reproducer']['networks']['pmacct_test_network']['ipv6_address'] = \
            repro_ip if len(params.test_subnet_ipv6)<1 else repro_ip.replace(params.test_subnet_ipv6, 'fd25::10')
        del data_dc['services']['traffic-reproducer']['networks']['pmacct_test_network']['ipv4_address']
    else:
        data_dc['services']['traffic-reproducer']['networks']['pmacct_test_network']['ipv4_address'] = \
            repro_ip if len(params.test_subnet_ipv4)<1 else repro_ip.replace(params.test_subnet_ipv4, '172.21.1.10')
        del data_dc['services']['traffic-reproducer']['networks']['pmacct_test_network']['ipv6_address']
    with open(results_pcap_folder + '/docker-compose.yml', 'w') as f:
        yaml.dump(data_dc, f, default_flow_style=False, sort_keys=False)

# Creates a pcap folder under the test results folder, where it copies traffic.pcap and traffic-reproducer.yml
# files. It also changes reproduction IP in traffic-reproducer.yml to that of the network framework and
# creates the docker-compose.yml for the specific container
def prepare_pcap_folder(params, i, test_config_file, test_pcap_file):
    results_pcap_folder = params.results_folder + '/pcap_mount_' + str(i)
    os.makedirs(results_pcap_folder)
    logger.debug('Created folder ' + short_name(results_pcap_folder))
    params.pcap_folders.append(results_pcap_folder)
    shutil.copy(test_config_file, results_pcap_folder + '/traffic-reproducer.yml')
    shutil.copy(test_pcap_file, results_pcap_folder + '/traffic.pcap')

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
    fill_repro_docker_compose(i, params, data['network']['map'][0]['repro_ip'], isIPv6)

    if isIPv6:
        fix_repro_ip_in_config(params.test_subnet_ipv6, data, 'fd25::10')
    else:
        fix_repro_ip_in_config(params.test_subnet_ipv4, data, '172.21.1.10')

    with open(results_pcap_folder + '/traffic-reproducer.yml', 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

# RUNS AFTER PMACCT IS RUN
# Prepares json output, log, pcap and pcap-config files
def prepare_pcap(_module):
    params = _module.testParams
    params.pcap_folders.clear()
    test_config_files = select_files(params.test_folder, 'traffic-reproducer.*-\\d+.yml$')
    test_pcap_files = select_files(params.test_folder, 'traffic.*-\\d+.pcap$')
    assert len(test_pcap_files)==len(test_config_files)

    # test_config_files is sorted per basename (filename)
    for i in range(len(test_config_files)):
        prepare_pcap_folder(params, i, test_config_files[i], test_pcap_files[i])

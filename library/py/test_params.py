###################################################
# Automated Testing Framework for Network Analytics
# Functions for preparing the environment for the
# test case to run in
# nikolaos.tsokas@swisscom.com 11/05/2023
###################################################

from library.py.helpers import select_files, read_config_file
import logging, os
logger = logging.getLogger(__name__)

class KPmacctParams:
    def __init__(self, main_results_folder, pmacct_name):
        self.name = pmacct_name
        self.daemon = pmacct_name.split('-')[0]
        self.results_folder = main_results_folder + '/' + pmacct_name
        self.docker_compose_file = self.results_folder + '/docker-compose-pmacct.yml'
        self.results_conf_file = self.results_folder + '/' + self.daemon + '.conf'
        self.results_mount_folder = self.results_folder + '/pmacct_mount'
        self.results_output_folder = self.results_mount_folder + '/pmacct_output'
        self.pmacct_log_file = self.results_output_folder + '/pmacctd.log'
        self.test_conf_file = None

class KModuleParams:
    def __init__(self, test_file, daemon='nfacctd', ipv4_subnet='', ipv6_subnet=''):
        self.daemon = daemon
        self.test_subnet_ipv4 = ipv4_subnet
        self.test_subnet_ipv6 = ipv6_subnet
        self.build_static_params(test_file)

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
        self.pcap_folders = self.output_files = self.log_files = []
        self.kafka_topics = {}

    @property
    def pmacct_log_file(self):
        return self.pmacct[0].pmacct_log_file

    @property
    def pmacct_name(self):
        return self.pmacct[0].name

    @property
    def results_mount_folder(self):
        return self.pmacct[0].results_mount_folder
    @property
    def results_conf_file(self):
        return self.pmacct[0].results_conf_file
    @property
    def pmacct_docker_compose_file(self):
        return self.pmacct[0].docker_compose_file

    def set_pmacct_params(self):
        self.pmacct = []
        index = 0
        for conffile in self.test_conf_files:
            index += 1
            basename = os.path.basename(conffile)
            pmacct = KPmacctParams(self.results_folder, basename.split('.conf')[0])
            pmacct.test_conf_file = conffile
            pmacct.ipv4 = '172.21.1.' + str(index) + '3'
            pmacct.ipv6 = 'fd25::' + str(index) + '3'
            self.pmacct.append(pmacct)

    # Dynamic params are built after it has been determined whether it is about a default
    # or about a specific scenario
    def build_dynamic_params(self, scenario):
        # default values, some may be overriden below for a scenario
        self.results_folder = os.getcwd() + '/results/' + self.test_name
        self.test_output_files = select_files(self.test_folder, 'output.*-\\d+.json$')
        self.test_log_files = select_files(self.test_folder, 'output.*-\\d+.txt$')
        self.test_conf_files = select_files(self.test_folder, self.daemon + '-\\d+.conf$')

        if scenario!='default':
            scenario_conf_files = select_files(self.test_folder + '/' + scenario, self.daemon + '-\\d+.conf$')
            scenario_output_files = select_files(self.test_folder + '/' + scenario, 'output.*-\\d+.json$')
            scenario_log_files = select_files(self.test_folder + '/' + scenario, 'output.*-\\d+.txt$')
            if len(scenario_conf_files)>0:
                self.test_conf_files = scenario_conf_files
            if len(scenario_output_files)>0:
                self.test_output_files = scenario_output_files
            if len(scenario_log_files)>0:
                self.test_log_files = scenario_log_files
            self.results_folder = os.getcwd() + '/results/' + self.test_name + '__' + scenario

        self.results_dump_folder = self.results_folder + '/kafka_dumps'

        logger.debug('Test config files: ' + str(self.test_conf_files))
        logger.debug('Test output files: ' + str(self.test_output_files))
        logger.debug('Test log files: ' + str(self.test_log_files))
        self.set_pmacct_params()

    # Returns the configuration object corresponding to the pmacct instance with the provided name
    def get_pmacct_with_name(self, pmacct_name):
        for p in self.pmacct:
            if p.name==pmacct_name:
                return p
        return None

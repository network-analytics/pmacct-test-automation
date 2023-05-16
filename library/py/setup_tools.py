
import logging, os, shutil, secrets
from library.py.helpers import *
logger = logging.getLogger(__name__)


class KModuleParams:
    def __init__(self, _module):
        self.build_static_params(_module.__file__)

    def build_static_params(self, filename):
        self.test_folder = os.path.dirname(filename)
        self.test_name = os.path.basename(self.test_folder)
        self.test_mount_folder = self.test_folder + '/pmacct_mount'
        self.test_conf_file = self.test_folder + '/pmacctd.conf'
        self.results_folder = os.getcwd() + '/results/' + self.test_name
        self.results_conf_file = self.results_folder + '/pmacctd.conf'
        self.results_mount_folder = self.results_folder + '/pmacct_mount'
        self.results_output_folder = self.results_mount_folder + '/pmacct_output'
        self.kafka_topic_name = 'test.topic.' + secrets.token_hex(4)[:8]
        self.results_log_file = self.results_output_folder + '/pmacctd.log'


# Prepares results folder to receive logs and output from pmacct
def prepare_test_env(_module):
    params = _module.testModuleParams
    config = _module.confFile
    logger.info('Test name: ' + params.test_name)

    # Make sure there's a pmacctd.conf file for pmacct configuration
    if not os.path.isfile(params.test_conf_file):
        return False
    logger.debug('Pmacct config file identified successfully')

    if os.path.exists(params.results_folder):
        logger.debug('Results folder exists, deleting')
        shutil.rmtree(params.results_folder)
    logger.info('Creating test mount folder: ' + params.results_mount_folder)
    os.makedirs(params.results_mount_folder)
    logger.info('Creating test output folder: ' + params.results_output_folder)
    _mask = os.umask(0)
    os.makedirs(params.results_output_folder, 0o777)
    os.umask(_mask)
    logger.debug('Folders created')

    # Edit configuration
    config.replace_value_of_key('logfile', '/var/log/pmacct/pmacct_output/pmacctd.log')
    config.replace_value_of_key('pidfile', '/var/log/pmacct/pmacct_output/pmacctd.pid')
    config.replace_value_of_key('kafka_topic', params.kafka_topic_name)
    config.replace_value_of_key('kafka_config_file', '/var/log/pmacct/librdkafka.conf')
    config.replace_value_of_key('kafka_avro_schema_registry', 'http://schema-registry:8081')
    # Later pmacct versions expect avro_schema_output_file instead of avro_schema_file
    config.replace_value_of_key('avro_schema_file', '/var/log/pmacct/pmacct_output/flow_avroschema.avsc')
    config.replace_value_of_key('debug', 'true')
    config.replace_value_of_key('pre_tag_map', '/var/log/pmacct/pretag.map')
    config.replace_value_of_key('flow_to_rd_map', '/var/log/pmacct/f2rd-00.map')
    config.replace_value_of_key('nfacctd_ip', '0.0.0.0')
    config.replace_value_of_key('nfacctd_port', '8989')
    config.replace_value_of_key('aggregate_primitives', '/var/log/pmacct/custom-primitives-00.lst')
    config.print_to_file(params.results_conf_file)

    # Copy existing files in pmacct_mount to result mount folder
    if os.path.exists(params.test_mount_folder):
        src_files = os.listdir(params.test_mount_folder)
        count = 0
        for file_name in src_files:
            full_file_name = os.path.join(params.test_mount_folder, file_name)
            if os.path.isfile(full_file_name) and not file_name.startswith('.'):
                count += 1
                logger.debug('Copying: ' + full_file_name)
                shutil.copy(full_file_name, params.results_mount_folder)
        logger.info('Copied ' + str(count) + ' files')
    return True
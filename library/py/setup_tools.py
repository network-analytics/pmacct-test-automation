
import logging, os, shutil, secrets
from library.py.helpers import *
logger = logging.getLogger(__name__)


class KModuleParams:
    def __init__(self, _module):
        self.test_folder = os.path.dirname(_module.__file__)
        self.test_name = os.path.basename(self.test_folder)
        self.test_mount_folder = self.test_folder + '/pmacct_mount'
        self.test_conf_file = self.test_folder + '/pmacctd.conf'
        self.results_folder = os.getcwd() + '/results/' + self.test_name
        self.results_conf_file = self.results_folder + '/pmacctd.conf'
        self.results_mount_folder = self.results_folder + '/pmacct_mount'
        self.results_output_folder = self.results_mount_folder + '/pmacct_output'
        self.original_kafka_topic_name = find_value_in_config_file(self.test_conf_file, 'kafka_topic')
        self.kafka_topic_name = self.original_kafka_topic_name + '.' + secrets.token_hex(4)[:8]
        self.original_log_file = find_value_in_config_file(self.test_conf_file, 'logfile')
        self.pmacct_local_log_file = '/var/log/pmacct/pmacct_output/pmacctd.log'
        self.results_log_file = self.results_output_folder + '/pmacctd.log'


# Prepares results folder to receive logs and output from pmacct
def prepare_test_env(_module):
    params = _module.testModuleParams
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

    # Copy pmacct config file to results folder
    logger.info('Copying pmacct conf file to results folder')
    logger.debug('From: ' + params.test_conf_file)
    logger.debug('To: ' + params.results_conf_file)
    shutil.copy(params.test_conf_file, params.results_conf_file)
    replace_in_file(params.results_conf_file, params.original_log_file, params.pmacct_local_log_file)
    logger.info('Changed log file name to: ' + params.pmacct_local_log_file)
    replace_in_file(params.results_conf_file, params.original_kafka_topic_name, params.kafka_topic_name)
    logger.info('Changed kafka topic name to: ' + params.kafka_topic_name)

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
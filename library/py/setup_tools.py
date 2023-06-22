
import library.py.scripts as scripts
import shutil, secrets
from library.py.helpers import *
from library.py.configuration_file import KConfigurationFile
logger = logging.getLogger(__name__)


class KModuleParams:
    def __init__(self, _module, pmacct_config_filename=''):
        self.pmacct_config_filename = pmacct_config_filename
        self.build_static_params(_module.__file__)

    def build_static_params(self, filename):
        self.test_folder = os.path.dirname(filename)
        self.test_name = os.path.basename(self.test_folder)
        self.test_mount_folder = self.test_folder + '/pmacct_mount'
        self.pmacct_mount_folder = '/var/log/pmacct'
        self.pmacct_output_folder = self.pmacct_mount_folder + '/pmacct_output'
        if self.pmacct_config_filename!='':
            self.test_conf_file = self.test_folder + '/' + self.pmacct_config_filename
        else:
            self.test_conf_file = self.test_folder + '/pmacctd.conf'
            if not os.path.isfile(self.test_conf_file):
                fnames = select_files(self.test_folder, 'nfacctd.+conf')
                assert len(fnames)==1
                self.test_conf_file = self.test_folder + '/' + fnames[0]
        self.results_folder = os.getcwd() + '/results/' + self.test_name
        self.results_conf_file = self.results_folder + '/pmacctd.conf'
        self.results_mount_folder = self.results_folder + '/pmacct_mount'
        self.results_output_folder = self.results_mount_folder + '/pmacct_output'
        self.kafka_topic_name = 'test.topic.' + secrets.token_hex(4)[:8]
        self.results_log_file = self.results_output_folder + '/pmacctd.log'
        self.results_msg_dump = self.results_folder + '/message_dump.json'
        self.pmacct_ip = None
        self.host_ip = None


# Prepares results folder to receive logs and output from pmacct
def prepare_test_env(_module):
    params = _module.testModuleParams
    config = _module.confFile
    logger.info('Test name: ' + params.test_name)

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

    # Preparing actual pmacctd.conf file

    # Files in mounted folder, for pmacct to read
    config.replace_value_of_key('kafka_config_file', params.pmacct_mount_folder + '/librdkafka.conf')
    config.replace_value_of_key('pre_tag_map', params.pmacct_mount_folder + '/pretag-00.map')
    config.replace_value_of_key('flow_to_rd_map', params.pmacct_mount_folder + '/f2rd-00.map')
    config.replace_value_of_key('aggregate_primitives', params.pmacct_mount_folder + '/custom-primitives-00.lst')

    # Files in output folder, for pmacct to write
    config.replace_value_of_key('logfile', params.pmacct_output_folder + '/pmacctd.log')
    config.replace_value_of_key('pidfile', params.pmacct_output_folder + '/pmacctd.pid')
    config.replace_value_of_key('avro_schema_output_file', params.pmacct_output_folder + '/flow_avroschema.avsc')

    # Replace specific operational values
    config.replace_value_of_key('kafka_topic', params.kafka_topic_name)
    config.replace_value_of_key('kafka_avro_schema_registry', 'http://schema-registry:8081')
    config.replace_value_of_key('debug', 'true')
    config.replace_value_of_key('nfacctd_ip', '0.0.0.0')
    config.replace_value_of_key('nfacctd_port', '8989')

    # Output to new conf file in mount folder
    config.print_to_file(params.results_conf_file)

    # Copy existing files in pmacct_mount to result (=actual) mounted folder
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

# Prepares json output, log, pcap and pcap-config files
def prepare_pcap(_module):
    params = _module.testModuleParams
    test_config_files = select_files(params.test_folder, 'traffic-reproducer.*-\d+.conf')
    test_pcap_files = select_files(params.test_folder, 'traffic.*-\d+.pcap')
    test_output_files = select_files(params.test_folder, 'output.*-\d+.json')
    test_log_files = select_files(params.test_folder, 'output.*-\d+.log')

    assert len(test_pcap_files)>0
    assert len(test_pcap_files)==len(test_config_files)
    assert len(test_output_files)>0

    def copyList(filelist):
        retVal = []
        for filename in filelist:
            retVal.append(params.results_folder + '/' + filename)
            shutil.copy(params.test_folder + '/' + filename, params.results_folder + '/' + filename)
        return retVal

    results_config_files = copyList(test_config_files)
    results_pcap_files = copyList(test_pcap_files)
    results_output_files = copyList(test_output_files)
    results_log_files = copyList(test_log_files)

    params.host_ip = scripts.find_host_ip()
    logger.info('Host pmacct_test_network IP: ' + params.host_ip)
    assert params.host_ip != None

    # Important to keep the indenting due to yaml notation
    for i in range(len(results_config_files)):
        confPcap = KConfigurationFile(results_config_files[i])
        confPcap.replace_value_of_key('pcap', results_pcap_files[i])
        #confPcap.replace_value_of_key('    repro_ip', params.host_ip) #'127.0.0.1')
        #confPcap.replace_value_of_key('    bgp_id', params.host_ip) #'127.0.0.1')
        #confPcap.replace_value_of_key('    ip', params.host_ip) #'127.0.0.1')
        confPcap.replace_value_of_key('    repro_ip', '127.0.0.1') # needs to be a valid IP of the host (127.0.0.1 or 192.168.x.x)
        confPcap.replace_value_of_key('    bgp_id', '1.1.1.' + str(i))
        confPcap.replace_value_of_key('    ip', '127.0.0.1')
        confPcap.replace_value_of_key('    port', '2929')
        confPcap.print_to_file(results_config_files[i])
    # repro_ip, bgp_id and ip work with both 127.0.0.1 and host ifconfig IP (e.g., 192.168.1.111)

    with open(params.results_mount_folder + '/pretag-00.map', 'w') as f:
        f.write("set_label=nkey%100.1%pkey%testing       ip="+params.host_ip+"/32\nset_label=nkey%unknown%pkey%unknown")

    # following didn't work (possibly because the order is changed when dumped back?)
    # import yaml
    # with open(pcap_config_file) as f:
    #     data = yaml.load(f, Loader=yaml.FullLoader)
    # data['network']['map'][0]['repro_ip'] = '127.0.0.1'
    # data['bmp']['collector']['ip'] = '127.0.0.1'
    # data['bmp']['collector']['port'] = '2929'
    # with open(pcap_config_file, 'w') as f:
    #     data = yaml.dump(data, f)

    return (results_config_files, results_output_files, results_log_files)
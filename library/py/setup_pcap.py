###################################################
# Automated Testing Framework for Network Analytics
# Functions for preparing the environment for the
# test case to run in - pcap part
# nikolaos.tsokas@swisscom.com 11/05/2023
###################################################

import shutil, secrets, logging, os, yaml
from library.py.configuration_file import KConfigurationFile
from library.py.test_params import KPmacctParams, KModuleParams
from typing import List, Dict
from library.py.helpers import short_name, select_files, replace_IPs, KFileList
logger = logging.getLogger(__name__)


# Fixes reproduction IP in a config object, if needed (if not, it only produces a log)
def fix_repro_ip_in_config(ip_subnet: str, config: Dict, fw_ip: str):
    if len(ip_subnet) < 1:
        logger.info('Reference subnet not set, assuming traffic reproduction IP from framework subnet')
    else:
        logger.info('Reference subnet set, setting traffic reproduction IP to framework subnet')
        config['network']['map'][0]['repro_ip'] = config['network']['map'][0]['repro_ip'].replace(ip_subnet, fw_ip)

# Creates docker-compose.yml file for a specific traffic-reproducer
def fill_repro_docker_compose(i: int, params: KModuleParams, repro_ip: str, isIPv6: bool):
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
def prepare_pcap_folder(params: KModuleParams, i: int, test_config_file: str, test_pcap_file: str):
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
def prepare_pcap(params: KModuleParams):
    params.pcap_folders.clear()
    test_config_files = select_files(params.test_folder, 'traffic-reproducer.*-\\d+.yml$')
    test_pcap_files = select_files(params.test_folder, 'traffic.*-\\d+.pcap$')
    assert len(test_pcap_files)==len(test_config_files)

    # test_config_files is sorted per basename (filename)
    for i in range(len(test_config_files)):
        prepare_pcap_folder(params, i, test_config_files[i], test_pcap_files[i])

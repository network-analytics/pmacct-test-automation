###################################################
# Automated Testing Framework for Network Analytics
# Functions for preparing the environment for the
# test case to run in - pcap part
# nikolaos.tsokas@swisscom.com 11/05/2023
###################################################

import shutil, logging, os, yaml
from library.py.test_params import KModuleParams
from typing import Dict
from library.py.helpers import short_name, get_reproduction_IP_and_BGP_ID
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
    os.makedirs(results_pcap_folder + '/pcap0')
    logger.debug('Created folder ' + short_name(results_pcap_folder + '/pcap0'))
    params.pcap_folders.append(results_pcap_folder)
    shutil.copy(test_config_file, results_pcap_folder + '/pcap0/traffic-reproducer.yml')
    shutil.copy(test_pcap_file, results_pcap_folder + '/pcap0/traffic.pcap')

    with open(results_pcap_folder + '/pcap0/traffic-reproducer.yml') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    data['pcap'] = '/pcap/pcap0/traffic.pcap'

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

    with open(results_pcap_folder + '/pcap0/traffic-reproducer.yml', 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

# RUNS AFTER PMACCT IS RUN
# Prepares json output, log, pcap and pcap-config files
def prepare_pcap(params: KModuleParams):
    params.pcap_folders.clear()
    # test_config_files = select_files(params.test_folder, 'traffic-reproducer.*-\\d+.yml$')
    # test_pcap_files = select_files(params.test_folder, 'traffic.*-\\d+.pcap$')
    # assert len(test_pcap_files)==len(test_config_files)

    # test_config_files is sorted per basename (filename)
    # for i in range(len(test_config_files)):
    #     prepare_pcap_folder(params, i, test_config_files[i], test_pcap_files[i])



    with open(params.test_folder + '/container-setup.yml') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    for container in data['containers']:
        folder_name = params.results_folder + '/' + container['name']
        os.makedirs(folder_name)
        params.traffic_folders.append(folder_name)

        # Make sure traffic-reproducer.yml files of all pcap folders refer to the same IP and BGP_ID
        # Otherwise, it is not possible for a single server (container) to replay these traffic data
        config_file_src = params.test_folder + '/' + container['processes'][0]['config']
        repro_info = get_reproduction_IP_and_BGP_ID(config_file_src)
        for i in range(len(container['processes'])):
            config_file_src = params.test_folder + '/' + container['processes'][i]['config']
            if repro_info != get_reproduction_IP_and_BGP_ID(config_file_src):
                logger.error('IP and/or BGP_ID for the same traffic reproducer do not match!')
                return None
        repro_ip = repro_info[0]
        isIPv6 = ':' in repro_info[0]

        with open(params.root_folder + '/library/sh/traffic_docker/docker-compose-template.yml') as f:
            data_dc = yaml.load(f, Loader=yaml.FullLoader)

        data_dc['services']['traffic-reproducer']['container_name'] = container['name']
        data_dc['services']['traffic-reproducer']['image'] = params.fw_config.get('TRAFFIC_REPRO_IMG')
        data_dc['services']['traffic-reproducer']['volumes'][0] = folder_name + ':/pcap'

        if isIPv6:
            data_dc['services']['traffic-reproducer']['networks']['pmacct_test_network']['ipv6_address'] = \
                repro_ip if len(params.test_subnet_ipv6) < 1 else repro_ip.replace(params.test_subnet_ipv6, 'fd25::10')
            del data_dc['services']['traffic-reproducer']['networks']['pmacct_test_network']['ipv4_address']
        else:
            data_dc['services']['traffic-reproducer']['networks']['pmacct_test_network']['ipv4_address'] = \
                repro_ip if len(params.test_subnet_ipv4) < 1 else repro_ip.replace(params.test_subnet_ipv4, '172.21.1.10')
            del data_dc['services']['traffic-reproducer']['networks']['pmacct_test_network']['ipv6_address']

        with open(folder_name + '/docker-compose.yml', 'w') as f:
            yaml.dump(data_dc, f, default_flow_style=False, sort_keys=False)

        for i in range(len(container['processes'])):
            process = container['processes'][i]
            pcap_file_src = params.test_folder + '/' + process['pcap']
            pcap_file_dst = folder_name + '/' + process['pcap']
            if not os.path.isfile(pcap_file_dst):
                shutil.copy(pcap_file_src, pcap_file_dst)
            os.makedirs(folder_name + '/pcap' + str(i))
            config_file_src = params.test_folder + '/' + process['config']
            config_file_dst = folder_name + '/pcap' + str(i) + '/traffic-reproducer.yml'
            shutil.copy(config_file_src, config_file_dst)
            with open(config_file_dst) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
            data['pcap'] = '/pcap/' + process['pcap']

            # adding pmacct IP address
            # isIPv6 = ':' in data['network']['map'][0]['repro_ip']
            pmacct = params.get_pmacct_with_name(process['collector'])
            pmacct_ip = pmacct.ipv6 if isIPv6 else pmacct.ipv4
            logger.debug('Traffic uses ' + ('IPv6' if isIPv6 else 'IPv4'))
            for k in ['bmp', 'bgp', 'ipfix']:
                if k in data:
                    data[k]['collector']['ip'] = pmacct_ip

            if isIPv6:
                fix_repro_ip_in_config(params.test_subnet_ipv6, data, 'fd25::10')
            else:
                fix_repro_ip_in_config(params.test_subnet_ipv4, data, '172.21.1.10')

            with open(folder_name + '/pcap' + str(i) + '/traffic-reproducer.yml', 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

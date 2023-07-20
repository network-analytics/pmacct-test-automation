###################################################
# Automated Testing Framework for Network Analytics
#
# python functions calling specific shell scripts
# and returning the outcome
#
###################################################

from library.py.script_tools import *
import re, logging, os, yaml
logger = logging.getLogger(__name__)


def create_test_network() -> bool:
    logger.info("Creating test network (pmacct_test_network)")
    return run_script(['./library/sh/test_network/create.sh'])[0]

# Starts Kafka containers using docker-compose and returns success or not
def start_kafka_containers() -> bool:
    logger.info("Starting Kafka containers")
    return run_script(['./library/sh/kafka_compose/start.sh'])[0]

# Starts pmacct container using docker run and returns success or not
# If the pmacct container exists, it removes it using docker rm (pmacct needs to have exited)
# It gets as input the full-path filename of the pmacct configuration file
def start_pmacct_container(pmacct_conf_file: str, pmacct_mount_folder_fullpath: str) -> bool: #, pmacct_ip: str) -> bool:
    logger.info("Starting pmacct container")
    return run_script(['./library/sh/pmacct_docker/start.sh', pmacct_conf_file, pmacct_mount_folder_fullpath])[0]

# Deletes pmacct_test_network while tearing-down
def delete_test_network() -> bool:
    logger.info("Deleting test network (pmacct_test_network)")
    return run_script(['./library/sh/test_network/delete.sh'])[0]

# Stops Kafka containers using docker-compose and returns success or not
def stop_and_remove_kafka_containers() -> bool:
    logger.info("Stopping Kafka containers")
    return run_script(['./library/sh/kafka_compose/stop.sh'])[0]

# Stops pmacct container using docker stop and docker rm and returns success or not
def stop_and_remove_pmacct_container() -> bool:
    logger.info("Stopping and removing pmacct container")
    return run_script(['./library/sh/pmacct_docker/stop.sh'])[0]

# Stops traffic-reproducer container using docker stop and docker rm and returns success or not
def stop_and_remove_traffic_container(traffic_id: int) -> bool:
    logger.info("Stopping and removing traffic container with ID: " + str(traffic_id))
    return run_script(['./library/sh/traffic_docker/stop.sh', str(traffic_id)])[0]

# Stops ALL traffic-reproducer containers using docker stop and docker rm and returns success or not
def stop_and_remove_all_traffic_containers() -> bool:
    logger.info("Stopping and removing all traffic containers")
    return run_script(['./library/sh/traffic_docker/stop_all.sh'])[0]

# Waits for pmacct container to be reported as running and return success or not
# seconds: maximum time to wait for pmacct
def wait_pmacct_running(seconds: int) -> bool:
    def checkfunction(out):
        return out[0] and not 'false' in out[1].lower()
    return wait_for_container('./library/sh/docker_tools/check-container-running.sh', 'pmacct', checkfunction, seconds)

# Checks if broker container is running or not and return boolean value
def check_broker_running() -> bool:
    logger.info("Checking if broker is running")
    return run_script(['./library/sh/docker_tools/check-container-running.sh', 'broker'])[0]

# Sends signal to container
def send_signal_to_pmacct(sig: str) -> bool:
    logger.info("Sending signal " + sig + " to pmacct")
    return run_script(['./library/sh/docker_tools/send-signal.sh', 'pmacct', sig])[0]

# Waits for schema-registry container to be reported as healthy and return success or not
# seconds: maximum time to wait for schema-registry
def wait_schemaregistry_healthy(seconds: int) -> bool:
    logger.info("Checking if schema-registry is healthy")
    def checkfunction(out):
        return out[0] and 'healthy' in out[1].lower()
    return wait_for_container('./library/sh/docker_tools/check-container-health.sh', 'schema-registry', checkfunction, seconds, 5)

# Clears Kafka topic by moving the low_watermark to the end of the messages. Returns success or failure.
# topic: the name of the topic to clear
def clear_kafka_topic(topic: str) -> bool:
    logger.info("Clearing topic " + topic)
    return run_script(['./library/sh/docker_tools/clear-topic.sh', topic])[0]

# Creates new Kafka topic. If it exists already, it clears/resets it.
# topic: name of the topic to create
# clearing/resetting functionality NOT thoroughly tested
def create_or_clear_kafka_topic(topic: str) -> bool:
    logger.info("Creating (or clearing) Kafka topic " + topic)
    out = run_script('./library/sh/docker_tools/list-topics.sh')
    if not out[0]:
        logger.info("Could not list existing topics")
        return False
    if topic in out[1]:
        logger.info("Topic exists already")
        retval = clear_kafka_topic(topic)
        if retval:
            logger.info("Topic cleared successfully")
        else:
            logger.info("Falied to clear topic")
        return retval
    logger.info("Creating Kafka topic " + topic)
    retval = run_script(['./library/sh/docker_tools/create-topic.sh', topic])[0]
    if retval:
        logger.info('Topic created successfully')
    else:
        logger.info('Failed to create topic')
    return retval

def replay_pcap_with_docker(pcap_mount_folder: str, ip_address: str, ipv6_address: str = None) -> bool:
    logger.info('Replaying pcap file from ' + pcap_mount_folder)
    logger.info('Container IP: ' + ip_address + ', IPv6: ' + str(ipv6_address))
    args = ['./library/sh/traffic_docker/start.sh', pcap_mount_folder, ip_address]
    if ipv6_address!=None:
        args.append(ipv6_address)
    success, output, error = run_script(args)
    logger.debug('Success: ' + str(success))
    if len(output)>0:
        lines = output.split('\n')
        for line in lines:
            logger.debug('Output: ' + line)
    if len(error):
        lines = error.split('\n')
        for line in lines:
            logger.debug('Error: ' + line)
    return success

def replay_pcap(pcap_mount_folder: str) -> bool:
    logger.info('Replaying pcap file from ' + pcap_mount_folder)

    with open(pcap_mount_folder + '/traffic-reproducer.conf') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    ip = data['network']['map'][0]['repro_ip']
    logger.info('Container IP: ' + ip)
    args = ['./library/sh/traffic_docker/start2.sh', pcap_mount_folder, ip]

    success, output, error = run_script(args)
    logger.debug('Success: ' + str(success))
    if len(output)>0:
        lines = output.split('\n')
        for line in lines:
            logger.debug('Output: ' + line)
    if len(error):
        lines = error.split('\n')
        for line in lines:
            logger.debug('Error: ' + line)
    return success

def replay_pcap_with_detached_docker(pcap_mount_folder: str, player_id: int, container_ip: str, ipv6_address: str = None) -> bool:
    logger.info('Replaying pcap file from ' + pcap_mount_folder + ' with DETACHED docker container')
    logger.debug('Container IP: ' + container_ip + ' Ipv6: ' + str(ipv6_address))
    args = ['./library/sh/traffic_docker/start_bg.sh', pcap_mount_folder, str(player_id), container_ip]
    if ipv6_address!=None:
         args.append(ipv6_address)
    return run_script(args)[0]
    # return run_script(['./library/sh/traffic_docker/start_bg.sh', pcap_mount_folder, str(player_id), container_ip])[0]

def replay_pcap_detached(pcap_mount_folder: str, player_id: int) -> bool:
    logger.info('Replaying pcap file from ' + pcap_mount_folder + ' with DETACHED docker container')

    with open(pcap_mount_folder + '/traffic-reproducer.conf') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    ip = data['network']['map'][0]['repro_ip']
    logger.info('Container IP: ' + ip)
    args = ['./library/sh/traffic_docker/start_bg2.sh', pcap_mount_folder, str(player_id), ip]

    return run_script(args)[0]

def replay_pcap_with_detached_docker_dual(pcap_mount_folder1: str, pcap_mount_folder2: str, player_id: int,
                                          container_ip: str, ipv6_address: str = None) -> bool:
    logger.info('Replaying dual pcap file from ' + pcap_mount_folder1 + ' and ' + pcap_mount_folder2 +
                ' with DETACHED docker container')
    logger.debug('Container IP: ' + container_ip + ' Ipv6: ' + str(ipv6_address))
    args = ['./library/sh/traffic_docker/start_bg_dual.sh', pcap_mount_folder1, pcap_mount_folder2, str(player_id),
            container_ip]
    if ipv6_address != None:
        args.append(ipv6_address)
    return run_script(args)[0]

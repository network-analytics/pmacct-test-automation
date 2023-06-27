###################################################
# Automated Testing Framework for Network Analytics
#
# python functions calling specific shell scripts
# and returning the outcome
#
###################################################

from library.py.script_tools import *
import re, logging, os
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
def start_pmacct_container(pmacct_conf_file: str, pmacct_mount_folder_fullpath: str, pmacct_ip: str) -> bool:
    logger.info("Starting pmacct container with IP: " + pmacct_ip)
    return run_script(['./library/sh/pmacct_docker/start.sh', pmacct_conf_file, pmacct_mount_folder_fullpath, pmacct_ip])[0]

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

# Find pmacct IP
# def find_pmacct_ip() -> str:
#     logger.info("Finding pmacct IP address")
#     return run_script(['./library/sh/docker_tools/find-container-ip.sh', 'pmacct'])[1]

# Find host (Gateway) IP
# def find_host_ip() -> str:
#     logger.info("Finding host IP address")
#     return run_script(['./library/sh/docker_tools/find-gateway-ip.sh'])[1]

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

def replay_pcap_with_docker(pcap_mount_folder: str, ip_address: str) -> bool:
    logger.info('Replaying pcap file from ' + pcap_mount_folder + ' with docker container (IP: ' + ip_address + ')')
    return run_script(['./library/sh/traffic_docker/start.sh', pcap_mount_folder, ip_address])[0]

def replay_pcap_with_detached_docker(pcap_mount_folder: str, player_id: int, container_ip: str) -> bool:
    logger.info('Replaying pcap file from ' + pcap_mount_folder + ' with detached docker container')
    logger.debug('Folder: ' + pcap_mount_folder + ' Player ID: ' + str(player_id) + ' Container IP: ' + container_ip)
    return run_script(['./library/sh/traffic_docker/start_bg.sh', pcap_mount_folder, str(player_id), container_ip])[0]

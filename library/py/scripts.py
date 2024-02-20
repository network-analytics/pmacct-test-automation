###################################################
# Automated Testing Framework for Network Analytics
# Python functions calling specific shell scripts
# and returning the outcome
# nikolaos.tsokas@swisscom.com 26/02/2023
###################################################

from library.py.script_tools import *
from library.py import helpers
import logging
logger = logging.getLogger(__name__)


def create_test_network() -> bool:
    logger.info("Creating test network (pmacct_test_network)")
    return run_script(['./library/sh/test_network/create.sh'])[0]

# Starts Kafka containers using docker-compose and returns success or not
def start_kafka_containers() -> bool:
    logger.info("Starting Kafka containers")
    return run_script(['./library/sh/kafka_compose/start.sh'])[0]

def start_pmacct_container(pmacct_name, pmacct_docker_compose_file: str) -> bool:
    logger.info("Starting pmacct container " + pmacct_name)
    return run_script(['./library/sh/pmacct_docker/start.sh', pmacct_docker_compose_file])[0]

# Starts Redis container
def start_redis_container() -> bool:
    logger.info("Starting Redis container")
    return run_script(['./library/sh/redis_docker/start.sh'])[0]

# Deletes pmacct_test_network while tearing-down
def delete_test_network() -> bool:
    logger.info("Deleting test network (pmacct_test_network)")
    return run_script(['./library/sh/test_network/delete.sh'])[0]

# Stops Kafka containers using docker-compose and returns success or not
def stop_and_remove_kafka_containers() -> bool:
    logger.info("Stopping Kafka containers")
    return run_script(['./library/sh/kafka_compose/stop.sh'])[0]

# Gets pmacct container stats
def get_pmacct_stats(pmacct_name: str) -> str:
    logger.info("Getting pmacct stats from docker for: " + pmacct_name)
    ret = run_script(['./library/sh/docker_tools/get-container-stats.sh', pmacct_name])
    if not ret[0]:
        return ret[2]
    return ret[1]

# Stops pmacct container using docker stop and docker rm and returns success or not
def stop_and_remove_pmacct_container(pmacct_name, pmacct_docker_compose_file: str) -> bool:
    logger.info("Stopping and removing pmacct container " + pmacct_name)
    return run_script(['./library/sh/pmacct_docker/stop.sh', pmacct_docker_compose_file])[0]

# Stops and removes Redis container
def stop_and_remove_redis_container() -> bool:
    logger.info("Stopping Redis container")
    return run_script(['./library/sh/redis_docker/stop.sh'])[0]

# Stops traffic-reproducer container using docker stop and docker rm and returns success or not
def stop_and_remove_traffic_container_byID(traffic_id) -> bool: # called with either int or str
    logger.info("Stopping and removing traffic container with ID: " + str(traffic_id))
    return run_script(['./library/sh/traffic_docker/stop.sh', str(traffic_id)])[0]

# Stops traffic-reproducer container using docker stop and docker rm and returns success or not
def stop_and_remove_traffic_container(pcap_folder: str) -> bool:
    logger.info("Stopping and removing traffic container of folder: " + helpers.short_name(pcap_folder))
    return run_script(['./library/sh/traffic_docker/stop_docker_compose.sh', pcap_folder + '/docker-compose.yml'])[0]

# Stops ALL traffic-reproducer containers using docker stop and docker rm and returns success or not
def stop_and_remove_all_traffic_containers() -> bool:
    logger.info("Stopping and removing all traffic containers")
    return run_script(['./library/sh/traffic_docker/stop_all.sh'])[0]

# Waits for pmacct container to be reported as running and return success or not
# seconds: maximum time to wait for pmacct
def wait_pmacct_running(pmacct_name: str, seconds: int) -> bool:
    def checkfunction(out):
        return out[0] and not 'false' in out[1].lower()
    return wait_for_container('./library/sh/docker_tools/check-container-running.sh', pmacct_name, checkfunction, seconds)

# Waits for redis container to be reported as running and return success or not
# seconds: maximum time to wait for pmacct
def wait_redis_running(seconds: int) -> bool:
    def checkfunction(out):
        return out[0] and 'pong' in out[1].lower()
    return wait_for_container('./library/sh/docker_tools/check-redis-running.sh', 'redis', checkfunction, seconds)

# Checks if broker container is running or not and return boolean value
def check_broker_running() -> bool:
    logger.info("Checking if Kafka broker is running")
    return run_script(['./library/sh/docker_tools/check-container-running.sh', 'broker'])[0]

# Sends signal to container
def send_signal_to_pmacct(pmacct_name: str, sig: str) -> bool:
    logger.info("Sending signal " + sig + " to container " + pmacct_name)
    return run_script(['./library/sh/docker_tools/send-signal.sh', pmacct_name, sig])[0]

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
    out = run_script('./library/sh/docker_tools/list-topics.sh')
    if not out[0]:
        logger.info("Could not list existing topics")
        return False
    if topic in out[1]:
        logger.info("Topic " + topic + " exists already")
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

def display_debug_info(success, output, error):
    logger.debug('Success: ' + str(success))
    if len(output) > 0:
        lines = output.split('\n')
        for line in lines:
            logger.debug('Output: ' + line)
    if not success and len(error):
        lines = error.split('\n')
        for line in lines:
            logger.debug('Error: ' + line)

# Spawns a new traffic reproducer container and replays traffic from folder pcap_mount_folder
# pcap_mount_folder is the path of the folder containing the docker-compose.yml file for the container
# in question; it typically contains also traffic reproduction information
def replay_pcap(pcap_mount_folder: str, detached: bool = False) -> bool:
    logger.info('Replaying pcap file from ' + pcap_mount_folder)
    args = ['./library/sh/traffic_docker/start_docker_compose.sh', pcap_mount_folder + '/docker-compose.yml']
    if detached==True:
        args.append('-d')
    success, output, error = run_script(args)
    display_debug_info(success, output, error)
    return success

# Spawns a new traffic reproducer container in detached mode and replays traffic from folder pcap_mount_folder
# pcap_mount_folder is the path of the folder containing the docker-compose.yml file for the container
# in question; it typically contains also traffic reproduction information
# def replay_pcap_detached(pcap_mount_folder: str) -> bool:
#     logger.info('Replaying pcap file from ' + helpers.short_name(pcap_mount_folder) + ' with DETACHED docker container')
#     args = ['./library/sh/traffic_docker/start_docker_compose.sh', pcap_mount_folder + '/docker-compose.yml', '-d']
#     success, output, error = run_script(args)
#     display_debug_info(success, output, error)
#     return success

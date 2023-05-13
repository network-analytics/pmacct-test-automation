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

# Starts Kafka containers using docker-compose and returns success or not
def start_kafka_containers() -> bool:
    logger.info("Starting Kafka containers")
    return run_script('./library/sh/kafka_compose/start.sh')[0]

# Starts pmacct container using docker run and returns success or not
# If the pmacct container exists, it removes it using docker rm (pmacct needs to have exited)
# It gets as input the full-path filename of the pmacct configuration file
def start_pmacct_container(pmacct_conf_file: str, pmacct_mount_folder_fullpath: str) -> bool:
    logger.info("Starting pmacct container")
    return run_script(['./library/sh/pmacct_docker/start.sh', pmacct_conf_file, pmacct_mount_folder_fullpath])[0]

# Stops Kafka containers using docker-compose and returns success or not
def stop_and_remove_kafka_containers() -> bool:
    logger.info("Stopping Kafka containers")
    return run_script('./library/sh/kafka_compose/stop.sh')[0]

# Stops pmacct container using docker stop and docker rm and returns success or not
def stop_and_remove_pmacct_container() -> bool:
    logger.info("Stopping and removing pmacct container")
    return run_script('./library/sh/pmacct_docker/stop.sh')[0]

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

# Sends IPFIX packets to pmacct. It returns the number of packets sent, or -1 upon failure
# Sending lasts as many seconds, as defined in "duration" (default 1 sec)
def send_ipfix_packets(duration: int = 1) -> int:
    logger.info('Sending IPFIX packets for smoke test')
    [success, output] = run_script(['python3', './traffic_generators/ipfix/play_ipfix_packets.py', '-S', '10.1.1.1', \
                                    '-D', str(duration), '-F', '15', '-C', '1', '-w', '10', '-p', '2929'])
    if not success:
        logger.info('Sending IPFIX packets failed')
        return -1
    matches = re.findall(r"(?<=Sent ).+(?= packets)", output)
    if len(matches)<1:
        logger.info('Could not determine how many IPFIX packets were sent')
        return -1
    logger.info('Sent ' + matches[0] + " IPFIX packets")
    return int(matches[0])

#
#
def replay_pcap_file(config_file_name: str) -> bool:
    logger.info('Replaying pcap file ' + os.path.basename(config_file_name))
    [success, output] = run_script(['python3', './traffic_generators/reproduction/main.py', '-t', \
                                    config_file_name]) #, '-v'])
    if not success:
        logger.info('Replaying failed')
    else:
        logger.info('Replaying succeeded')
    return success


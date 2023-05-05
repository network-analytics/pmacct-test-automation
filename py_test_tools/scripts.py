###################################################
# Automated Testing Framework for Network Analytics
#
# python functions calling specific shell scripts
# and returning the outcome
#
###################################################

from py_test_tools.script_tools import *
import re, logging, os
logger = logging.getLogger(__name__)

# Starts Kafka containers using docker-compose and returns success or not
def start_kafka_containers() -> bool:
    logging.info("Starting Kafka containers")
    return run_script('./sh_test_tools/kafka_compose/start.sh')[0]

# Starts pmacct container using docker run and returns success or not
# If the pmacct container exists, it removes it using docker rm (pmacct needs to have exited)
# It gets as input the full-path filename of the pmacct configuration file
def start_pmacct_container(pmacct_conf_file: str, pmacct_mount_folder_fullpath: str) -> bool:
    logging.info("Starting pmacct container")
    return run_script(['./sh_test_tools/pmacct_docker/start.sh', pmacct_conf_file, pmacct_mount_folder_fullpath])[0]

# Stops Kafka containers using docker-compose and returns success or not
def stop_and_remove_kafka_containers() -> bool:
    logging.info("Stopping Kafka containers")
    return run_script('./sh_test_tools/kafka_compose/stop.sh')[0]

# Stops pmacct container using docker stop and docker rm and returns success or not
def stop_and_remove_pmacct_container() -> bool:
    logging.info("Stopping and removing pmacct container")
    return run_script('./sh_test_tools/pmacct_docker/stop.sh')[0]

# Waits for pmacct container to be reported as running and return success or not
# seconds: maximum time to wait for pmacct
def wait_pmacct_running(seconds: int) -> bool:
    def checkfunction(out):
        return out[0] and not 'false' in out[1].lower()
    return wait_for_container('./sh_test_tools/docker_tools/check-container-running.sh', 'pmacct', checkfunction, seconds)

# Checks if broker container is running or not and return boolean value
def check_broker_running() -> bool:
    logging.info("Checking if broker is running")
    return run_script(['./sh_test_tools/docker_tools/check-container-running.sh', 'broker'])[0]

# Sends signal to container
def send_signal_to_pmacct(sig: str) -> bool:
    logging.info("Sending signal " + sig + " to pmacct")
    return run_script(['./sh_test_tools/docker_tools/send-signal.sh', 'pmacct', sig])[0]

# Waits for schema-registry container to be reported as healthy and return success or not
# seconds: maximum time to wait for schema-registry
def wait_schemaregistry_healthy(seconds: int) -> bool:
    logging.info("Checking if schema-registry is healthy")
    def checkfunction(out):
        return out[0] and 'healthy' in out[1].lower()
    return wait_for_container('./sh_test_tools/docker_tools/check-container-health.sh', 'schema-registry', checkfunction, seconds, 5)

# Clears Kafka topic by moving the low_watermark to the end of the messages. Returns success or failure.
# topic: the name of the topic to clear
def clear_kafka_topic(topic: str) -> bool:
    logging.info("Clearing topic " + topic)
    return run_script(['./sh_test_tools/docker_tools/clear-topic.sh', topic])[0]

# Creates new Kafka topic. If it exists already, it clears/resets it.
# topic: name of the topic to create
def create_or_clear_kafka_topic(topic: str) -> bool:
    logging.info("Creating (or clearing) Kafka topic " + topic)
    out = run_script('./sh_test_tools/docker_tools/list-topics.sh')
    if not out[0]:
        logging.info("Could not list existing topics")
        return False
    if topic in out[1]:
        logging.info("Topic exists already")
        retval = clear_kafka_topic(topic)
        if retval:
            logging.info("Topic cleared successfully")
        else:
            logging.info("Falied to clear topic")
        return retval
    logging.info("Creating Kafka topic " + topic)
    retval = run_script(['./sh_test_tools/docker_tools/create-topic.sh', topic])[0]
    if retval:
        logging.info('Topic created successfully')
    else:
        logging.info('Failed to create topic')
    return retval

# Sends IPFIX packets to pmacct for smoke test purposes. It returns the number of packets sent, or -1 upon failure
# Sending lasts 10 seconds
def send_smoketest_ipfix_packets() -> int:
    logging.info('Sending IPFIX packets for smoke test')
    [success, output] = run_script(['python3', './traffic_generators/ipfix/play_ipfix_packets.py', '-S', '10.1.1.1', \
                                    '-D', '10', '-F', '15', '-C', '1', '-w', '10', '-p', '2929'])
    if not success:
        logging.info('Sending IPFIX packets failed')
        return -1
    matches = re.findall(r"(?<=Sent ).+(?= packets)", output)
    if len(matches)<1:
        logging.info('Could not determine how many IPFIX packets were sent')
        return -1
    logging.info('Sent ' + matches[0] + " IPFIX packets")
    return int(matches[0])

# Sends IPFIX packets to pmacct for test purposes. It returns the number of packets sent, or -1 upon failure
# Sending lasts 1 second
def send_1sec_ipfix_packets() -> int:
    logging.info('Sending IPFIX packets for 1 second')
    [success, output] = run_script(['python3', './traffic_generators/ipfix/play_ipfix_packets.py', '-S', '10.1.1.1', \
                                    '-D', '1', '-F', '15', '-C', '1', '-w', '10', '-p', '2929'])
    if not success:
        logging.info('Sending IPFIX packets failed')
        return -1
    matches = re.findall(r"(?<=Sent ).+(?= packets)", output)
    if len(matches)<1:
        logging.info('Could not determine how many IPFIX packets were sent')
        return -1
    logging.info('Sent ' + matches[0] + " IPFIX packets")
    return int(matches[0])

# Checks for text in pmacct logs
def check_file_for_text(filename: str, txt: str) -> bool:
    logging.info("Checking file " + os.path.basename(filename) + " for text \"" + txt + "\"")
    retVal = run_script(['grep', txt, filename])[0]
    if retVal:
        logging.info("Text \"" + txt + "\" found!")
    return run_script(['grep', txt, filename])[0]
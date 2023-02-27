
from py_test_tools.script_tools import *
import re


def start_kafka_containers():
    print("Starting Kafka containers")
    return run_script('./sh_test_tools/kafka_compose/start.sh')[0]

def start_pmacct_container(pmacct_conf_file):
    print("Starting pmacct container")
    return run_script(['./sh_test_tools/pmacct_docker/start.sh', pmacct_conf_file])[0]

def stop_and_remove_kafka_containers():
    print("Stopping Kafka containers")
    return run_script('./sh_test_tools/kafka_compose/stop.sh')[0]

def stop_and_remove_pmacct_container():
    print("Stopping and removing pmacct container")
    return run_script('./sh_test_tools/pmacct_docker/stop.sh')[0]

def wait_pmacct_running(seconds):
    def checkfunction(out):
        return out[0] and not 'false' in out[1].lower()
    return wait_for_container('./sh_test_tools/docker_tools/check-container-running.sh', 'pmacct', checkfunction, seconds)

def check_broker_running():
    print("Checking if broker is running")
    return run_script(['./sh_test_tools/docker_tools/check-container-running.sh', 'broker'])[0]

def wait_schemaregistry_healthy(seconds):
    print("Checking if schema-registry is healthy")
    def checkfunction(out):
        return out[0] and 'healthy' in out[1].lower()
    return wait_for_container('./sh_test_tools/docker_tools/check-container-health.sh', 'schema-registry', checkfunction, seconds, 5)

def clear_kafka_topic(topic):
    print("Clearing topic " + topic)
    return run_script(['./sh_test_tools/docker_tools/clear-topic.sh', topic])[0]

def create_or_clear_kafka_topic(topic):
    print("Creating (or clearing) Kafka topic " + topic)
    out = run_script('./sh_test_tools/docker_tools/list-topics.sh')
    if not out[0]:
        print("Could not list existing topics")
        return False
    if topic in out[1]:
        print("Topic exists already")
        retval = clear_kafka_topic(topic)
        if retval:
            print("Topic cleared successfully")
        else:
            print("Falied to clear topic")
        return retval
    print("Creating Kafka topic " + topic)
    retval = run_script(['./sh_test_tools/docker_tools/create-topic.sh', topic])[0]
    if retval:
        print('Topic created successfully')
    else:
        print('Failed to create topic')
    return retval

def send_smoketest_ipfix_packets():
    print('Sending IPFIX packets for smoke test')
    [success, output] = run_script(['python3', './traffic_generators/ipfix/play_ipfix_packets.py', '-S', '10.1.1.1', \
                                    '-D', '10', '-F', '15', '-C', '1', '-w', '10', '-p', '2929'])
    if not success:
        print('Sending IPFIX packets failed')
        return -1
    matches = re.findall(r"(?<=Sent ).+(?= packets)", output)
    if len(matches)<1:
        print('Could not determine how many IPFIX packets were sent')
        return -1
    print('Sent ' + matches[0] + " IPFIX packets")
    return int(matches[0])


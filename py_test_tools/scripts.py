
from py_test_tools.script_tools import *
import re


def start_kafka_containers():
    return run_script('./sh_test_tools/kafka_compose/start.sh')[0]

def start_pmacct_container(pmacct_conf_file):
    return run_script(['./sh_test_tools/pmacct_docker/start.sh', pmacct_conf_file])[0]

def stop_and_remove_kafka_containers():
    return run_script('./sh_test_tools/kafka_compose/stop.sh')[0]

def stop_and_remove_pmacct_container():
    return run_script('./sh_test_tools/pmacct_docker/stop.sh')[0]

def wait_pmacct_running(seconds):
    def checkfunction(out):
        return len(out)>1 and out[0] and not 'false' in out[1].lower()
    return wait_for_container('./sh_test_tools/docker_tools/check-container-running.sh', 'pmacct', checkfunction, seconds)

def wait_schemaregistry_healthy(seconds):
    def checkfunction(out):
        return len(out)>1 and out[0] and 'healthy' in out[1].lower()
    return wait_for_container('./sh_test_tools/docker_tools/check-container-health.sh', 'schema-registry', checkfunction, seconds, 5)

def create_daisy_topic(topic):
    out = run_script(['./sh_test_tools/docker_tools/create-topic.sh', topic])
    if len(out)<1 or not out[0]:
        print('Topic creation failed')
        return False
    existsAlready = False
    if 'returned non-zero exit status' in out[1]:
        existsAlready = True
    out = run_script('./sh_test_tools/docker_tools/list-topics.sh')
    retval = len(out)>1 and out[0] and topic in out[1]
    if retval:
        if existsAlready:
            print ('Topic exists already')
        else:
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


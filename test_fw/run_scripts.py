
import subprocess
import time
import re


def run_script(command):
    try:
#        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
        result = subprocess.run(command, stdout=subprocess.PIPE, check=True)
        output = result.stdout.decode('utf-8').strip()
        success = result.returncode==0
    except Exception:
        output = None
        success = False
    return [success, output]


def start_kafka_containers():
    return run_script('./kafka-compose/start.sh')[0]

def start_pmacct_container():
    return run_script('./pmacct-docker/start.sh')[0]

def stop_kafka_containers():
    return run_script('./kafka-compose/stop.sh')[0]

def stop_pmacct_container():
    return run_script('./pmacct-docker/stop.sh')[0]

def wait_for_container(command, name, checkfunc, seconds, sec_update=1):
    print('Waiting for ' + name + ' to be functional')
    out = run_script([command, name])
    while not checkfunc(out):
        seconds -= 1
        if seconds < 0:
            print(name + ' check timed out')
            return False
        time.sleep(1)
        if seconds % sec_update == 0:
            print('Still waiting for ' + name + '...')
        out = run_script([command, name])
    print(name + ' is up and running')
    return True

def wait_pmacct_running(seconds):
    def checkfunction(out):
        return out[0] and not 'false' in out[1].lower()
    return wait_for_container('docker-tools/check-container-running.sh', 'pmacct', checkfunction, seconds)

def wait_schemaregistry_healthy(seconds):
    def checkfunction(out):
        return out[0] and 'healthy' in out[1].lower()
    return wait_for_container('docker-tools/check-container-health.sh', 'schema-registry', checkfunction, seconds, 5)

def send_ipfix_packets():
    print('Sending IPFIX packets for smoke test')
    [success, output] = run_script(['python3', 'traffic-generators/ipfix/play_ipfix_packets.py', '-S', '10.1.1.1', \
                                    '-D', '10', '-F', '15', '-C', '1', '-w', '10', '-p', '2929'])
    if not success:
        print('Sending IPFIX packets failed')
        return False
    matches = re.findall(r"(?<=Sent ).+(?= packets)", output)
    if len(matches)<1:
        print('Could not determine how many IPFIX packets were sent')
        return False
    print('Sent ' + matches[0] + " IPFIX packets")
    return True


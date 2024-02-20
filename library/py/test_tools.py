###################################################
# Automated Testing Framework for Network Analytics
# Highest-level test functions for test cases to
# reuse repeatable/common functionality
# nikolaos.tsokas@swisscom.com 07/07/2023
###################################################

import logging, os, secrets, yaml, shutil, time, datetime
import library.py.json_tools as jsontools
import library.py.helpers as helpers
import library.py.escape_regex as escape_regex
import library.py.setup_test as setup_test
import library.py.scripts as scripts
from library.py.kafka_consumer import KMessageReader
from library.py.test_params import KModuleParams
from typing import List
logger = logging.getLogger(__name__)



class KTestHelper:

    def __init__(self, testParams: KModuleParams, consumers):
        self.params = testParams
        self.consumers = consumers
        self.ignored_fields = []

    def spawn_traffic_container(self, container_name: str, detached: bool = False):
        logger.debug('Traffic folders: ' + str(self.params.traffic_folders))
        pcap_folder = self.params.traffic_folders.getFileLike(container_name)
        return scripts.replay_pcap(pcap_folder, detached)

    def delete_traffic_container(self, container_name: str):
        pcap_folder = self.params.traffic_folders.getFileLike(container_name)
        return scripts.stop_and_remove_traffic_container(pcap_folder)

    def set_ignored_fields(self, ignored_fields):
        self.ignored_fields = ignored_fields

    def read_and_compare_messages(self, topic_name: str,  reference_json: str, wait_time: int = 120):
        consumer = self.consumers.getReaderOfTopicStartingWith(topic_name)
        return read_and_compare_messages(consumer, self.params, reference_json, self.ignored_fields, wait_time)

    def transform_log_file(self, log_tag: str, name: str):
        logfile = self.params.log_files.getFileLike(log_tag)
        repro_info = helpers.get_reproduction_IP_and_BGP_ID(self.params.traffic_folders.getFileLike(name) +
                                                            '/pcap0/traffic-reproducer.yml')
        transform_log_file(logfile, repro_info[0])

    def check_file_regex_sequence_in_pmacct_log(self, log_tag: str, pmacct_name: str = None):
        logfile = self.params.log_files.getFileLike(log_tag)
        pmacct = self.params.get_pmacct_with_name(pmacct_name) if pmacct_name else self.params.pmacct[0]
        return helpers.check_file_regex_sequence_in_file(pmacct.pmacct_log_file, logfile)

    def check_regex_sequence_in_pmacct_log(self, regexes: List, pmacct_name: str = None):
        pmacct = self.params.get_pmacct_with_name(pmacct_name) if pmacct_name else self.params.pmacct[0]
        return helpers.check_regex_sequence_in_file(pmacct.pmacct_log_file, regexes)

    def wait_and_check_logs(self, log_tag: str, max_seconds: int, seconds_repeat: int):
        logfile = self.params.log_files.getFileLike(log_tag)
        return helpers.retry_until_true('Checking expected logs',
                lambda: helpers.check_file_regex_sequence_in_file(self.params.pmacct_log_file, logfile),
                                        max_seconds, seconds_repeat)

    def check_regex_in_pmacct_log(self, regex: str, pmacct_name: str = None):
        pmacct = self.params.get_pmacct_with_name(pmacct_name) if pmacct_name else self.params.pmacct[0]
        return helpers.check_regex_sequence_in_file(pmacct.pmacct_log_file, [regex])




def replace_IPs_and_get_reference_file(params: KModuleParams, json_name: str):
    # Replacing IP addresses in output json file with the ones anticipated from pmacct
    output_json_file = params.output_files.getFileLike(json_name)
    helpers.replace_IPs(params, output_json_file)
    logger.info('Using reference file ' + helpers.short_name(output_json_file))
    return output_json_file


# Reads messages from Kafka topic and compares with given file. First argument is the Kafka consumer object,
# which will be used for reading. The number of messages anticipated is equal to the number of non-empty
# lines of the json file passed as second argument. The latter is first edited in terms of referenced IPs,
# as per the ip_subst_pairs, which are pairs of IPs, representing which IPs must be replaced by which.
def read_and_compare_messages(consumer: KMessageReader, params: KModuleParams, json_name: str,
                              ignore_fields: List, wait_time: int = 120):
    output_json_file = replace_IPs_and_get_reference_file(params, json_name)
    # Counting non empty json lines in output file, so that we know the number of anticipated messages
    line_count = helpers.count_non_empty_lines(output_json_file)
    logger.info('Expecting ' + str(line_count) + ' messages')

    # Reading messages from Kafka topic
    # Max wait time for line_count messages is 120 seconds by default (overriden in arguments)
    # The get_messages method will return only if either line_count messages are received,
    # or 120 seconds have passed
    messages = consumer.get_messages(wait_time, line_count)
    if len(messages) < 1:
        logger.warning('No messages read by kafka consumer in ' + str(wait_time) + ' second(s)')
        return False
    elif len(messages) < line_count:
        logger.warning('Received ' + str(len(messages)) + ' messages instead of ' + str(line_count))
        return False
    elif line_count == len(messages):
        logger.info('Received the expected number of messages (' + str(len(messages)) + ')')
    else:
        logger.error('Received more messages than expected')
        return False

    # Comparing the received messages with the anticipated ones
    # output_json_file is a file (filename) with json lines
    logger.info('Comparing messages received with json lines in file ' + helpers.short_name(output_json_file))
    return jsontools.compare_messages_to_json_file(messages, output_json_file, ignore_fields)


# Reads all messages from Kafka topic within a specified timeout (wait_time)
# --> used for test-case development
def read_messages_dump_only(consumer: KMessageReader, params: KModuleParams, wait_time: int = 120):
    logger.info('Consuming from kafka [timeout=' + str(wait_time) + 's] and dumping messages in ' + params.results_dump_folder)

    # Reading messages from Kafka topic
    # The get_all_messages_timeout method consumes all messages and returns 
    # when wait_time (default=120s) has passed
    messages = consumer.get_messages(wait_time)
    if len(messages) < 1:
        logger.warning('No messages read by kafka consumer in ' + str(wait_time) + ' second(s)')
        return False

    logger.info('Consumed ' + str(len(messages)) + ' messages')
    logger.warning('Json comparing disabled (test-case development)!')

    return True 


# Replays traffic from a pcap folder to a specific running instance of pmacct. It can either run the traffic
# container in detached mode or not (default is not) - Not sufficiently tested
# def replay_pcap_to_collector(pcap_folder, pmacct, detached=False):
#     with open(pcap_folder + '/traffic-reproducer.yml') as f:
#         data = yaml.load(f, Loader=yaml.FullLoader)
#     # adding pmacct IP address
#     isIPv6 = ':' in data['network']['map'][0]['repro_ip']
#     pmacct_ip = pmacct.ipv6 if isIPv6 else pmacct.ipv4
#     for k in ['bmp', 'bgp', 'ipfix']:
#         if k in data:
#             data[k]['collector']['ip'] = pmacct_ip
#     with open(pcap_folder + '/traffic-reproducer.yml', 'w') as f:
#         yaml.dump(data, f, default_flow_style=False, sort_keys=False)
#     logger.info('Edited traffic-reproducer.yml with collector IP: ' + pmacct_ip)
#     return scripts.replay_pcap(pcap_folder) if detached==False else scripts.replay_pcap_detached(pcap_folder, 0)


# Clones the traffic files as many times as the number of pmacct instances, replaces in each traffic-repro.yml the
# corresponding pmacct IP, then mounts the pcap folders to a traffic reproducer container
def prepare_multicollector_pcap_player(results_folder: str, pcap_mount_folder: str, pmacct_list: List):
    # Make sure traffic-reproducer.yml files of all pcap folders refer to the same IP and BGP_ID
    # Otherwise, it is not possible for a single server (container) to replay these traffic data
    repro_info = helpers.get_REPRO_IP_and_BGP_ID(pcap_mount_folder)
    prefix = os.path.basename(pcap_mount_folder).split('_')[-1] + 'x' + str(len(pmacct_list))
    pcap_folder = results_folder + '/pcap_mount_' + prefix + '_multi'
    os.makedirs(pcap_folder)
    logger.info('Created following common mount pcap folder: ' + helpers.short_name(pcap_folder))

    logger.info('Pcap player repro info: ' + str(repro_info))
    logger.debug('Editing pcap folders and copying them together')
    for i in range(len(pmacct_list)):
        dst = pcap_folder + '/pcap' + str(i)
        shutil.copytree(pcap_mount_folder + '/pcap0', dst)
        with open(dst + '/traffic-reproducer.yml') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        # adding pmacct IP address
        isIPv6 = ':' in data['network']['map'][0]['repro_ip']
        pmacct_ip = pmacct_list[i].ipv6 if isIPv6 else pmacct_list[i].ipv4
        for k in ['bmp', 'bgp', 'ipfix']:
            if k in data:
                data[k]['collector']['ip'] = pmacct_ip
        with open(dst + '/traffic-reproducer.yml', 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        helpers.replace_in_file(dst + '/traffic-reproducer.yml', '/pcap/pcap0/traffic.pcap',
                                '/pcap/pcap' + str(i) + '/traffic.pcap')

    setup_test.build_compose_file_for_multitraffic_container(pcap_mount_folder, pcap_folder, 'traffic-reproducer-' +
                                                  prefix, len(pmacct_list))

    return pcap_folder


def prepare_multitraffic_pcap_player(results_folder: str, pcap_mount_folders: List):
    folder_names = ', '.join([helpers.short_name(folder) for folder in pcap_mount_folders])
    logger.info('Preparing multi-pcap player container...')
    logger.info('Creating common mount pcap folder for folders: ' + folder_names)

    # Make sure traffic-reproducer.yml files of all pcap folders refer to the same IP and BGP_ID
    # Otherwise, it is not possible for a single server (container) to replay these traffic data
    repro_info = helpers.get_REPRO_IP_and_BGP_ID(pcap_mount_folders[0])
    for i in range(1, len(pcap_mount_folders)):
        if repro_info != helpers.get_REPRO_IP_and_BGP_ID(pcap_mount_folders[i]):
            logger.error('IP and/or BGP_ID for the same traffic reproducer do not match!')
            return None

    pcap_folders_indices = [os.path.basename(folder).split('_')[-1] for folder in pcap_mount_folders]
    prefix = '-'.join(pcap_folders_indices)
    pcap_folder = results_folder + '/pcap_mount_' + prefix + '_multi'
    os.makedirs(pcap_folder)
    logger.info('Created following common mount pcap folder: ' + helpers.short_name(pcap_folder))

    logger.info('Pcap player repro info: ' + str(repro_info))
    logger.debug('Editing pcap folders and copying them together')
    for i in range(len(pcap_mount_folders)):
        dst = pcap_folder + '/pcap' + str(i)
        shutil.copytree(pcap_mount_folders[i] + '/pcap0', dst)
        helpers.replace_in_file(dst + '/traffic-reproducer.yml', '/pcap/pcap0/traffic.pcap',
                                '/pcap/pcap' + str(i) + '/traffic.pcap')

    setup_test.build_compose_file_for_multitraffic_container(pcap_mount_folders[0], pcap_folder, 'traffic-reproducer-' +
                                                  prefix, len(pcap_mount_folders))

    return pcap_folder


# Transforms a provided log file, in terms of regex syntax and IP substitutions
# repro_ip can be a regular expression
def transform_log_file(filename: str, repro_ip: str = None):
    token_ip = None
    if repro_ip and helpers.file_contains_string(filename, '${repro_ip}'):
        token_ip = secrets.token_hex(4)[:8]
        helpers.replace_in_file(filename, '${repro_ip}', token_ip)
    token1 = secrets.token_hex(4)[:8]
    if helpers.file_contains_string(filename, '${TIMESTAMP}'):
        helpers.replace_in_file(filename, '${TIMESTAMP}', token1)
    if helpers.file_contains_string(filename, '${IGNORE_REST}'):
        helpers.replace_in_file(filename, '${IGNORE_REST}', '')
    token2 = secrets.token_hex(4)[:8]
    if helpers.file_contains_string(filename, '${RANDOM}'):
        helpers.replace_in_file(filename, '${RANDOM}', token2)
    escape_regex.escape_file(filename)
    if helpers.file_contains_string(filename, token1):
        helpers.replace_in_file(filename, token1, '\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z')
    if helpers.file_contains_string(filename, token2):
        helpers.replace_in_file(filename, token2, '.+')
    if token_ip:
        helpers.replace_in_file(filename, token_ip, repro_ip)

# def transform_log_file(filename: str, repro_ip: str = None, bgp_id: str = None):
#     if repro_ip and helpers.file_contains_string(filename, '${repro_ip}'):
#         helpers.replace_in_file(filename, '${repro_ip}', repro_ip)
#     if bgp_id and helpers.file_contains_string(filename, '${bgp_id}'):
#         helpers.replace_in_file(filename, '${bgp_id}', bgp_id)
#     token1 = secrets.token_hex(4)[:8]
#     if helpers.file_contains_string(filename, '${TIMESTAMP}'):
#         helpers.replace_in_file(filename, '${TIMESTAMP}', token1)
#     if helpers.file_contains_string(filename, '${IGNORE_REST}'):
#         helpers.replace_in_file(filename, '${IGNORE_REST}', '')
#     token2 = secrets.token_hex(4)[:8]
#     if helpers.file_contains_string(filename, '${RANDOM}'):
#         helpers.replace_in_file(filename, '${RANDOM}', token2)
#     escape_regex.escape_file(filename)
#     if helpers.file_contains_string(filename, token1):
#         helpers.replace_in_file(filename, token1, '\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z')
#     if helpers.file_contains_string(filename, token2):
#         helpers.replace_in_file(filename, token2, '.+')


# Checks current second and, if needed, waits until the sleep period ends.
# Example: a process needs to finish by hh:mm:15 (=end_of_period) and it can take up to 30 seconds (=length).
# This means it must not start if seconds are greater than 45 or smaller than 15, until time goes hh:mm:15.
def avoid_time_period_in_seconds(end_of_period: int, length: int):
    if length>60:
        raise Exception('Avoided time period longer than 1 minute (must be <= 60sec)')

    curr_sec = datetime.datetime.now().second
    logger.info('Current minute seconds: ' + str(curr_sec))

    start_of_period = end_of_period - length
    if start_of_period>=0:
        if start_of_period <= curr_sec < end_of_period:
            wait_sec = end_of_period - curr_sec
        else:
            wait_sec = 0
    else:
        start_of_period += 60
        if curr_sec < end_of_period:
            wait_sec = end_of_period - curr_sec
        elif curr_sec > start_of_period:
            wait_sec = 60 - curr_sec + end_of_period
        else:
            wait_sec = 0

    if wait_sec<1:
        logger.debug('No need to wait')
    else:
        logger.debug('Waiting ' + str(wait_sec) + ' seconds')
        time.sleep(wait_sec)


# Waits until the next occurrence of second, i.e., until the time gets hh:mm:second. If current time happens
# to be equal to hh:mm:second, no wait time is applied and the function returns immediately
def wait_until_second(second: int):
    avoid_time_period_in_seconds(second, 60)

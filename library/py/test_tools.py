###################################################
# Automated Testing Framework for Network Analytics
# Highest-level test functions for test cases to
# reuse repeatable/common functionality
# nikolaos.tsokas@swisscom.com 07/07/2023
###################################################

import logging, os, secrets, yaml, shutil
import library.py.json_tools as jsontools
import library.py.helpers as helpers
import library.py.escape_regex as escape_regex
logger = logging.getLogger(__name__)

# Reads messages from Kafka topic and compares with given file. First argument is the Kafka consumer object,
# which will be used for reading. The number of messages anticipated is equal to the number of non-empty
# lines of the json file passed as second argument. The latter is first edited in terms of referenced IPs,
# as per the ip_subst_pairs, which are pairs of IPs, representing which IPs must be replaced by which.
def read_and_compare_messages(consumer, params, json_name, ignore_fields, wait_time=120):
    # Replacing IP addresses in output json file with the ones anticipated from pmacct
    output_json_file = params.output_files.getFileLike(json_name)
    params.replace_IPs(output_json_file)

    # Counting non empty json lines in output file, so that we know the number of anticipated messages
    line_count = helpers.count_non_empty_lines(output_json_file)

    logger.info('Using json file ' + helpers.short_name(output_json_file) + ', expecting ' + \
                str(line_count) + ' messages')
    # os.path.basename(output_json_file)

    # Reading messages from Kafka topic
    # Max wait time for line_count messages is 120 seconds by default (overriden in arguments)
    # The get_messages method will return only if either line_count messages are received,
    # or 120 seconds have passed
    messages = consumer.get_messages(wait_time, line_count)

    # Analytic log messages produced by the get_messages method
    if messages == None:
        return False

    # Comparing the received messages with the anticipated ones
    # output_json_file is a file (filename) with json lines
    logger.info('Comparing messages received with json lines in file ' + helpers.short_name(output_json_file))
    return jsontools.compare_messages_to_json_file(messages, output_json_file, ignore_fields)

def prepare_multi_pcap_player(results_folder, pcap_mount_folders):
    folder_names = ', '.join([helpers.short_name(folder) for folder in pcap_mount_folders])
    logger.info('Preparing multi-pcap player container...')
    logger.info('Creating common mount pcap folder for folders: ' + folder_names)

    def getREPROIPandBGPID(pcap_mount_folder):
        with open(pcap_mount_folder + '/traffic-reproducer.conf') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        repro_info = [data['network']['map'][0]['repro_ip'], None]
        if 'bgp_id' in data['network']['map'][0]:
            repro_info[1] = data['network']['map'][0]['bgp_id']
        return repro_info

    repro_info = getREPROIPandBGPID(pcap_mount_folders[0])
    for i in range(1, len(pcap_mount_folders)):
        if repro_info != getREPROIPandBGPID(pcap_mount_folders[i]):
            logger.error('IP and/or BGP_ID for the same player do not match!')
            return None

    pcap_folder = results_folder + '/pcap_mount_' + secrets.token_hex(4)[:8]
    os.makedirs(pcap_folder)
    logger.info('Created following common mount pcap folder: ' + helpers.short_name(pcap_folder))

    logger.info('Pcap player repro info: ' + str(repro_info))
    logger.debug('Editing pcap folders and copying them together')
    for i in range(len(pcap_mount_folders)):
        dst = pcap_folder + '/pcap' + str(i)
        shutil.copytree(pcap_mount_folders[i], dst)
        helpers.replace_in_file(dst + '/traffic-reproducer.conf', '/pcap/traffic.pcap',
                                '/pcap/pcap' + str(i) + '/traffic.pcap')

    return pcap_folder



# Transforms a provided log file, in terms of regex syntax and IP substitutions
def transform_log_file(filename, repro_ip=None, bgp_id=None):
    if repro_ip and helpers.file_contains_string(filename, '${repro_ip}'):
        helpers.replace_in_file(filename, '${repro_ip}', repro_ip)
    if bgp_id and helpers.file_contains_string(filename, '${bgp_id}'):
        helpers.replace_in_file(filename, '${bgp_id}', bgp_id)
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

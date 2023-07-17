###################################################
# Automated Testing Framework for Network Analytics
#
# Highest level test functions for reusing
# repeatable test case functionality
#
###################################################

import logging, os, secrets
import library.py.json_tools as jsontools
import library.py.helpers as helpers
import library.py.escape_regex as escape_regex
logger = logging.getLogger(__name__)

# Reads messages from Kafka topic and compares with given file. First argument is the Kafka consumer object,
# which will be used for reading. The number of messages anticipated is equal to the number of non-empty
# lines of the json file passed as second argument. The latter is first edited in terms of referenced IPs,
# as per the ip_subst_pairs, which are pairs of IPs, representing which IPs must be replaced by which.
def read_and_compare_messages(consumer, output_json_file, ip_subst_pairs, ignore_fields, wait_time=120):
    # Replacing IP addresses in output json file with the ones anticipated from pmacct
    for pair in ip_subst_pairs:
        helpers.replace_in_file(output_json_file, pair[0], pair[1])

    # Counting non empty json lines in output file, so that we know the number of anticipated messages
    line_count = helpers.count_non_empty_lines(output_json_file)

    logger.info('Using json file ' + os.path.basename(output_json_file) + ', expecting ' + \
                str(line_count) + ' messages')

    # Reading messages from Kafka topic
    # Max wait time for line_count messages is 120 seconds
    # The get_messages method will return only if either line_count messages are received,
    # or 120 seconds have passed
    messages = consumer.get_messages(wait_time, line_count)

    # Analytic log messages produced by the get_messages method
    if messages == None:
        return False

    # Comparing the received messages with the anticipated ones
    # output_json_file is a file (filename) with json lines
    return jsontools.compare_messages_to_json_file(messages, output_json_file, ignore_fields)

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
        helpers.replace_in_file(filename, token1, '\\d{4}\-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z')
    if helpers.file_contains_string(filename, token2):
        helpers.replace_in_file(filename, token2, '.+')

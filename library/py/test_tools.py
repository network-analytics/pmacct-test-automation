###################################################
# Automated Testing Framework for Network Analytics
#
# functions for preparing the environment for the
# test case to run in
#
###################################################

import logging, os
import library.py.json_tools as jsontools
import library.py.helpers as helpers
logger = logging.getLogger(__name__)


def read_and_compare_messages(consumer, output_json_file, ip_subst_pairs, ignore_fields):
    for pair in ip_subst_pairs:
        helpers.replace_in_file(output_json_file, pair[0], pair[1])
    line_count = helpers.count_non_empty_lines(output_json_file)
    logger.info('Using json file ' + os.path.basename(output_json_file) + ', expecting ' + str(line_count) + ' messages')
    messages = consumer.get_messages(120, line_count)
    if messages == None or len(messages) == 0:
        return False
    return jsontools.compare_messages_to_json_file(messages, output_json_file, ignore_fields)


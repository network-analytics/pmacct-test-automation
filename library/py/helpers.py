###################################################
# Automated Testing Framework for Network Analytics
#
# helpers file for python auxiliary functions
#
###################################################
import os
import re, time, logging, fileinput
import shutil

logger = logging.getLogger(__name__)

# # Message printing decorator for the tests
# def log_message(msg: str) -> str:
#     def decorator(fun):
#         def wrapper(*args, **kwargs):
#             #print('\033[94m' + fun.__name__ + '\033[0m' + ': ' + msg)
#             logger.info('\033[94m' + fun.__name__ + '\033[0m' + ': ' + msg)
#             return fun(*args, **kwargs)
#         return wrapper
#     return decorator

# Gets a pmacct configuration filename as input and returns the name of the Kafka topic
def find_kafka_topic_name(filename: str) -> str:
    return find_value_in_config_file(filename, 'kafka_topic')

def find_value_in_config_file(filename: str, keyname: str) -> str:
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            if '#' in line:
                line = line.split('#')[0].strip()
                if len(line)<1:
                    continue
            if '!' in line:
                line = line.split('!')[0].strip()
                if len(line) < 1:
                    continue
            matches = re.findall(r"(?<=" + keyname + ": ).+", line)
            if len(matches) > 0:
                return matches[0]
    return None

def get_current_time_in_milliseconds() -> int:
    return round(time.time()*1000)

def check_regex_sequence_in_file(file_path, regexes):
    logger.debug('Checking file ' + file_path + ' for patterns ' + str(regexes))
    with open(file_path, 'r') as file:
        text = file.read()
        start = 0
        for pattern in regexes:
            match = re.search(pattern, text[start:])
            if not match:
                return False
            start = match.end()
        return True

def replace_in_file(filename, search_pattern, replace_pattern):
    logger.debug('Replacing ' + search_pattern + ' with ' + replace_pattern + ' in file ' + filename)
    with open(filename) as f:
        lines = f.readlines()
    with open(filename + '.bak', 'w') as f:
        for line in lines:
            f.write(line.replace(search_pattern, replace_pattern))
    os.rename(filename + '.bak', filename)

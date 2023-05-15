###################################################
# Automated Testing Framework for Network Analytics
#
# helpers file for python auxiliary functions
#
###################################################
import os
import re, time, logging

logger = logging.getLogger(__name__)

#
#
def find_value_in_config_file(filename: str, keyname: str) -> str:
    relevant_lines = []
    with open(filename) as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
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
            return matches[0].strip()
        # Handling plugins
        if line.startswith(keyname):
            parts = line.split('[')
            if len(parts)>1 and parts[0]==keyname:
                parts = line.split(':')
                if len(parts)>1:
                    return parts[1].strip()
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

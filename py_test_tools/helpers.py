###################################################
# Automated Testing Framework for Network Analytics
#
# helpers file for python auxiliary functions
#
###################################################

import re, time, logging, json
logger = logging.getLogger(__name__)

# Message printing decorator for the tests
def log_message(msg: str) -> str:
    def decorator(fun):
        def wrapper(*args, **kwargs):
            #print('\033[94m' + fun.__name__ + '\033[0m' + ': ' + msg)
            logger.info('\033[94m' + fun.__name__ + '\033[0m' + ': ' + msg)
            return fun(*args, **kwargs)
        return wrapper
    return decorator

# TODO Replace with new function find_value_in_config_file
# Gets a pmacct configuration filename as input and returns the name of the Kafka topic
def find_kafka_topic_name(filename: str) -> str:
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
            matches = re.findall(r"(?<=kafka_topic: ).+", line)
            if len(matches) > 0:
                return matches[0]
    return None

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

def compare_json_files(file1_path, file2_path):
    with open(file1_path) as file1, open(file2_path) as file2:
        json1 = json.load(file1)
        json2 = json.load(file2)

    return compare_json_objects(json1, json2)

def compare_json_objects(json1, json2):
    if isinstance(json1, dict) and isinstance(json2, dict):
        keys1 = set(json1.keys())
        keys2 = set(json2.keys())
        common_keys = keys1.intersection(keys2)
        added_keys = keys2 - keys1
        removed_keys = keys1 - keys2
        differences = {}
        for key in common_keys:
            nested_diff = compare_json_objects(json1[key], json2[key])
            if nested_diff:
                differences[key] = nested_diff
        for key in added_keys:
            differences[key] = {'added': json2[key]}
        for key in removed_keys:
            differences[key] = {'removed': json1[key]}
        return differences if differences else None
    elif isinstance(json1, list) and isinstance(json2, list):
        if len(json1) != len(json2):
            return {'length': {'before': len(json1), 'after': len(json2)}}
        differences = []
        for i in range(len(json1)):
            nested_diff = compare_json_objects(json1[i], json2[i])
            if nested_diff:
                differences.append(nested_diff)
        return differences if differences else None
    else:
        if json1 != json2:
            return {'value': {'before': json1, 'after': json2}}
        return None



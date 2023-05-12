###################################################
# Automated Testing Framework for Network Analytics
#
# helpers file for python auxiliary functions
#
###################################################

import logging, json
logger = logging.getLogger(__name__)

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

def is_part_of_json(dict_part, dict_whole):
    logger.debug('Checking if json: ' + json.dumps(dict_part))
    logger.debug('is part of json: ' + json.dumps(dict_whole))
    part = json.dumps(dict_part, sort_keys=True)
    whole = json.dumps(dict_whole, sort_keys=True)
    if len(part)<3 or len(whole)<3:
        return False
    return part[1:-1] in whole[1:-1]
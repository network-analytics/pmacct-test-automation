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

# Compares json messages received (json1) with json lines expected (json2)
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
            differences[key] = {'missing': json2[key]}
        for key in removed_keys:
            differences[key] = {'got unknown': json1[key]}
        return differences if differences else None
    elif isinstance(json1, list) and isinstance(json2, list):
        if len(json1) != len(json2):
            return {'length': {'got': len(json1), 'expected': len(json2)}}
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

def are_json_identical(json1, json2):
    return json.dumps(json1, sort_keys=True)==json.dumps(json2, sort_keys=True)

def is_part_of_json(dict_part, dict_whole):
    logger.debug('Checking if json: ' + json.dumps(dict_part))
    logger.debug('is part of json: ' + json.dumps(dict_whole))
    part = json.dumps(dict_part, sort_keys=True)
    whole = json.dumps(dict_whole, sort_keys=True)
    if len(part)<3 or len(whole)<3:
        return False
    return part[1:-1] in whole[1:-1]

def compare_json_lists(json_list1, json_list2, ignore_fields=None, ignore_jsonpaths=None):
    json_list1 = [x.strip() for x in json_list1 if len(x)>3]
    json_list2 = [x.strip() for x in json_list2 if len(x)>3]
    logger.info('Comparing json lists (lengtjs: ' + str(len(json_list1)) + ', ' + str(len(json_list2)) + ')')
    if len(json_list1)!=len(json_list2):
        logger.info('Json lists have different sizes')
        return False
    for index in range(len(json_list1)):
        json1 = json.loads(json_list1[index])
        json2 = json.loads(json_list2[index])
        logger.debug('Comparing: ' + json_list1[index])
        logger.debug('With:      ' + json_list2[index])
        diff = compare_json_ignore(json1, json2, ignore_fields, ignore_jsonpaths)
        if diff:
            logger.info('Json not equal: ' + str(diff))
            return False
    logger.info('All json equal')
    return True

def compare_json_ignore(json1, json2, ignore_fields=None, ignore_jsonpaths=None):
    if ignore_fields:
        for field in ignore_fields:
            json1.pop(field, None)
            json2.pop(field, None)
    if ignore_jsonpaths:
        for jsonpath in ignore_jsonpaths:
            keys = jsonpath.strip('/').split('/')
            temp_json1 = json1
            temp_json2 = json2
            for key in keys[:-1]:
                temp_json1 = temp_json1.get(key, {})
                temp_json2 = temp_json2.get(key, {})
            temp_json1.pop(keys[-1], None)
            temp_json2.pop(keys[-1], None)
    return compare_json_objects(json1, json2)

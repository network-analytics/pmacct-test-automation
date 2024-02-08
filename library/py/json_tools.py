###################################################
# Automated Testing Framework for Network Analytics
# json tools commonly used by framework functions
# nikolaos.tsokas@swisscom.com 26/02/2023
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
            return {'value': {'received': json1, 'expected': json2}}
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

# Compares two json objects, which have been deprived of potentially irrelevant fields (to be ignored)
def compare_json_ignore(json1, json2, ignore_fields=None):
    if ignore_fields:
        for field in ignore_fields:
            json1.pop(field, None)
            json2.pop(field, None)
    return compare_json_objects(json1, json2)

# Compares two lists of json structures (strings), by optionally ignoring some (top-level) fields
# Every json object of the first list (json_list1) is checked against the full json_list2. If there's
# match, regardless of the order, the lines are considered as matching. The comparison fails at the first
# occurrence of a line in json_list1 not matching any object in json_list2
def compare_json_lists(json_list1, json_list2, ignore_fields=None):
    json_list1 = [json.loads(x.strip()) for x in json_list1 if len(x)>3]
    json_list2 = [json.loads(x.strip()) for x in json_list2 if len(x)>3]
    logger.info('Comparing json lists (lengths: ' + str(len(json_list1)) + ', ' + str(len(json_list2)) + ')')
    if len(json_list1)!=len(json_list2):
        logger.info('Json lists have different sizes')
        return False
    while len(json_list1):
        json1 = json_list1.pop(0)
        logger.debug('Matching: ' + str(json1))
        index = 0
        min_diff, min_diff_len, min_diff_index = -1, 1000000000, -1
        json2 = json_list2[index]
        diff = compare_json_ignore(json1, json2, ignore_fields)
        while diff:
            if len(diff)<min_diff_len:
                min_diff, min_diff_len, min_diff_index = diff, len(diff), index
            index += 1
            if index>=len(json_list2):
                logger.info('Received message not matched: ' + str(json1))
                logger.info('Closest match: ' + str(json_list2[min_diff_index]))
                logger.info('Closest match delta: ' + str(min_diff))
                return False
            json2 = json_list2[index]
            diff = compare_json_ignore(json1, json2, ignore_fields)
        logger.debug('Json matched')
        json_list2.pop(index)
    logger.info('All json matched')
    return True

def compare_json_lists_multi_match(json_list1, json_list2, ignore_fields=None, max_matches=-1):
    json_list1_len = len(json_list1)
    json_list1 = [json.loads(x.strip()) for x in json_list1 if len(x)>3]
    json_list2 = [json.loads(x.strip()) for x in json_list2 if len(x)>3]
    json_list2_occurrences = [0] * len(json_list2)
    logger.info('Comparing json lists (lengths: ' + str(len(json_list1)) + ', ' + str(len(json_list2)) + ')')
    while len(json_list1):
        json1 = json_list1.pop(0)
        logger.debug('Matching: ' + str(json1))
        index = 0
        min_diff, min_diff_len, min_diff_index = -1, 1000000000, -1
        json2 = json_list2[index]
        diff = compare_json_ignore(json1, json2, ignore_fields)
        while diff:
            if len(diff)<min_diff_len:
                min_diff, min_diff_len, min_diff_index = diff, len(diff), index
            index += 1
            if index>=len(json_list2):
                logger.info('Received message not matched: ' + str(json1))
                logger.info('Closest match: ' + str(json_list2[min_diff_index]))
                logger.info('Closest match delta: ' + str(min_diff))
                return False
            json2 = json_list2[index]
            diff = compare_json_ignore(json1, json2, ignore_fields)
        logger.debug('Json matched')
        json_list2_occurrences[index] = json_list2_occurrences[index] + 1
        if max_matches>-1 and json_list2_occurrences[index]>max_matches:
            logger.info('Json file line was matched more times than allowed (' + str(json_list2_occurrences[index]) +
                        ' instead of ' + str(max_matches) + ')')
            return False
    logger.info('All ' + str(json_list1_len) + ' received messages matched to json lines')
    dst_unmatched = 0
    for i in range(len(json_list2_occurrences)):
        if json_list2_occurrences[i]<1:
            dst_unmatched += 1
            logger.debug('Json file line not matched: ' + str(json_list2[i]))
    if dst_unmatched>0:
        logger.info(str(dst_unmatched) + ' json file lines were not matched to any received message')
        return False
    logger.info('All ' + str(len(json_list2)) + ' json file lines matched to received messages')
    return True

# Compares a list of dictionaries, which correspond to the messages received from Kafka,
# with the lines of a file, which depict json structures
def compare_messages_to_json_file(message_dicts, jsonfile, ignore_fields=None, multi_match_allowed=False):
    with open(jsonfile) as f:
        lines = f.readlines()
    jsons = [json.dumps(msg) for msg in message_dicts]
    if multi_match_allowed:
        return compare_json_lists_multi_match(jsons, lines, ignore_fields, 3)
    # return compare_json_lists_multi_match(jsons, lines, ignore_fields, 1)
    return compare_json_lists(jsons, lines, ignore_fields)

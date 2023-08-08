###################################################
# Automated Testing Framework for Network Analytics
#
# class representing a pmacct configuration file
#
###################################################

import re, logging
from typing import List, Dict
logger = logging.getLogger(__name__)

class KConfigurationFile:
    def __init__(self, filename: str):
        self.data = {}
        self.read_conf_file(filename)

    def read_conf_file(self, filename: str):
        self.data = {}
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if '#' in line:
                    line = line.split('#')[0].strip()
                if '!' in line:
                    line = line.split('!')[0].strip()
                if len(line) < 1:
                    continue
                if ':' in line:
                    key_value = line.split(':', 1)
                    key = key_value[0].strip()
                    value = key_value[1].strip()
                    match = re.match(r'^([^\[]+)\[([^\]]+)\]', key)
                    if match:
                        main_key = match.group(1)
                        sub_key = match.group(2)
                    else:
                        main_key = key
                        sub_key = ''
                    if main_key not in self.data:
                        self.data[main_key] = {}
                    self.data[main_key][sub_key] = value

    # subkey='' means all subkey values will be replaced
    def replace_value_of_key(self, key: str, value:str, subkey: str=None) -> bool:
        if key not in self.data:
            return False
        if len(self.data[key])<1:
            return False
        for sk in self.data[key]:
            if subkey is None or sk==subkey:
                self.data[key][sk] = value
        return True

    def replace_value_of_key_ending_with(self, key_ending: str, value:str, subkey: str=None) -> bool:
        for key in self.data.keys():
            if key.endswith(key_ending):
                for sk in self.data[key]:
                    if subkey is None or sk==subkey:
                        self.data[key][sk] = value
        return True

    def get_kafka_topics(self) -> Dict:
        retVal = {}
        for propname in self.data.keys():
            if propname.endswith('kafka_topic'):
                if len(self.data[propname].keys())>1:
                    raise Exception('Encountered two kafka topics with same key and different subkeys')
                retVal[propname] = list(self.data[propname].values())[0]
        return retVal

    def print_key_to_stringlist(self, key: str) -> List[str]:
        lines = []
        for k in self.data[key]:
            if k=='':
                lines.append(key + ': ' + self.data[key][k])
            else:
                lines.append(key + '[' + k + ']: ' + self.data[key][k])
        return lines

    def print_to_file(self, filename: str):
        logger.debug('Dumping configuration to file: ' + filename)
        with open(filename, 'w') as f:
            for key in self.data:
                lines = self.print_key_to_stringlist(key)
                for line in lines:
                    f.write(line + '\n')

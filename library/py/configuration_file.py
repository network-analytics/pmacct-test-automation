
import re, logging
logger = logging.getLogger(__name__)

def count_spaces(line: str) -> int:
    count = 0
    while line.startswith(' '):
        count += 1
        line = line[1:]
    return count

class KConfigurationFile:
    def __init__(self, filename: str):
        self.data = {}
        self.read_conf_file(filename)

    # Changed all strips to right-only strips, to keep indentation (important in traffic-repro.conf)
    def read_conf_file(self, filename: str):
        self.data = {}
        with open(filename, 'r') as file:
            for line in file:
                indent = count_spaces(line)
                line = line.rstrip()
                if '#' in line:
                    line = line.split('#')[0].rstrip()
                if '!' in line:
                    line = line.split('!')[0].rstrip()
                if len(line) < 1:
                    continue
                if ':' in line:
                    key_value = line.split(':', 1)
                    key = key_value[0].rstrip()
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

    # subkey='' means all subkeys values will be replaced
    def replace_value_of_key(self, key: str, value:str, subkey: str=None) -> bool:
        if key not in self.data:
            return False
        if len(self.data[key])<1:
            return False
        for sk in self.data[key]:
            if subkey is None or sk==subkey:
                self.data[key][sk] = value
        return True

    def uses_ipv6(self) -> bool:
        if '    repro_ip' not in self.data:
            return False
        return ':' in self.data['    repro_ip']['']

    def print_key_to_stringlist(self, key):
        lines = []
        for k in self.data[key]:
            if k=='':
                lines.append(key + ': ' + self.data[key][k])
            else:
                lines.append(key + '[' + k + ']: ' + self.data[key][k])
        return lines

    def print_to_file(self, filename):
        logger.debug('Dumping configuration to file: ' + filename)
        with open(filename, 'w') as f:
            for key in self.data:
                lines = self.print_key_to_stringlist(key)
                for line in lines:
                    f.write(line + '\n')

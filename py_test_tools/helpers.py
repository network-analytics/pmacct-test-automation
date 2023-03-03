###################################################
# Automated Testing Framework for Network Analytics
#
# helpers file for python auxiliary functions
#
###################################################

import re, time, logging
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

# Gets a pmacct configuration filename as input and returns the name of the Kafka topic
def find_kafka_topic_name(filename: str) -> str:
    with open(filename) as f:
        content = f.read()
        matches = re.findall(r"(?<=kafka_topic: ).+", content)
    if len(matches)<1:
        return None
    return matches[0]

def get_current_time_in_milliseconds() -> int:
    return round(time.time()*1000)
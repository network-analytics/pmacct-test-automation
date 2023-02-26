
import re

# message printing decorator for the test file
def print_message(msg):
    def decorator(fun):
        def wrapper(*args, **kwargs):
            print('\033[94m' + fun.__name__ + '\033[0m' + ': ' + msg)
            return fun(*args, **kwargs)
        return wrapper
    return decorator


def find_kafka_topic_name(filename):
    with open(filename) as f:
        content = f.read()
        matches = re.findall(r"(?<=kafka_topic: ).+", content)
    if len(matches)<1:
        return None
    return matches[0]



def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before the method call")
        result = func(*args, **kwargs)
        print("After the method call")
        return result
    return wrapper
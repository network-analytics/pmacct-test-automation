
def print_message(msg):
    def decorator(fun):
        def wrapper(*args, **kwargs):
            print('\033[91m' + fun.__name__ + '\033[0m' + ': ' + msg)
            return fun(*args, **kwargs)
        return wrapper
    return decorator


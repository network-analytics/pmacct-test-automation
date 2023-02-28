###################################################
# Automated Testing Framework for Network Analytics
#
# functions for calling shell scripts and for
# returning the outcome
#
###################################################

import subprocess
import time
from typing import List, Callable, Tuple


# Runs the command and returns a tuple of its result (success or not) and the message output
# command: a list of strings, first of which is the called script, the rest being the arguments
def run_script(command: List[str]) -> (bool, str):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8').strip()
        success = result.returncode==0
    except Exception as e:
        output = 'Exception thrown' + str(e)
        success = False
    return (success, output)


# Runs a script, which waits for a container to reach a certain state, for a maximum of time
# If the maximum time is reached without the state having been reached, it returns False. Otherwise True.
# command: a list of strings, first of which is the called script, the rest being the arguments
# name: the name of the container
# checkfunc: the function that checks whether the desired state has been reached. It takes as input a
#    tuple of the form (bool, str) and returns True or False, in terms of the state having been reached or not
def wait_for_container(command: List[str], name: str, checkfunc: Callable[[Tuple[bool, str]], bool], seconds: int, \
                       sec_update: int =1) -> bool:
    print('Waiting for ' + name + ' to be functional')
    out = run_script([command, name])
    while not checkfunc(out):
        seconds -= 1
        if seconds < 0:
            print(name + ' check timed out')
            return False
        time.sleep(1)
        if seconds % sec_update == 0:
            print('Still waiting for ' + name + '...')
        out = run_script([command, name])
    print(name + ' is up and running')
    return True

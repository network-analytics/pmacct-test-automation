
import subprocess
import time


def run_script(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, check=True)
        output = result.stdout.decode('utf-8').strip()
        success = result.returncode==0
    except subprocess.CalledProcessError as e:
        output = str(e)
        success = 'returned non-zero exit status' in output
    except Exception as e:
        output = 'Exception thrown' + str(e)
        success = False
    return [success, output]


def wait_for_container(command, name, checkfunc, seconds, sec_update=1):
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

## Test Description (902-log-rotation-signal)

IMPORTANT: not working at the moment (SIGHUP signal cannot be delivered to pmacct in the docker container). Need debugging...

Testing log rotation functionality: when logfile is moved to another location (e.g. to be archived), we need to send a signal to pmacct s.t. it will recreate the logfile and continue writing to it.

### Provided files:
```
- 902_test.py                    pytest file defining test execution

- nfacctd-00.conf                nfacctd daemon configuration file            HINT: you might want to change redis_ip

- output-log-00.txt              log messages that need to be in the logfile
- output-log-01.txt              log messages that need to be in the logfile
```

### Test proceeding and result:

1. Part 1: 

- start nfacctd normally
- check log messages in "output-log-00.txt" and verify that they are present in the logfile (order of appearence preserved, but there could/will be other logs in between) --> as long as this is successful you can proceed to part 2
- No ERROR or WARN messages are present in the logfile

2. Part 2:

- delete or move logfile
- send signal to reopen logging infrastructure

    kill -s SIGHUP <nfacctd-proc-id>

Then verify the following:

- Log file was successfully recreated
- Log messages in "output-log-00.txt" are also present in the re-created logfile (order of appearence preserved, but there could/will be other logs in between)

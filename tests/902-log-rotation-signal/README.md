## Test Description (902-log-rotation-signal)

Testing log rotation functionality: when logfile is moved to another location (e.g. to be archived), we need to send a signal to pmacct s.t. it will recreate the logfile and continue writing to it.

### Provided files:

- nfacctd-00.conf                nfacctd daemon configuration file            HINT: you might want to change redis_ip
- librdkafka-00.conf             librdkafka configuration for nfacctd

- output-log-00.log            log messages that need to be in the logfile                                  HINT: contains variable parameters
- output-log-01.log            log messages that need to be in the logfile                                  HINT: contains variable parameters

### Test proceeding and result:

1. Part 1: 

- start nfacctd normally
- check log messages in "output-log-00.log" and verify that they are present in the logfile (order of appearence preserved, but there could/will be other logs in between) --> as long as this is successful you can proceed to part 2
- No ERROR or WARN/WARNING messages are present in the logfile

2. Part 2:

- delete or move logfile
- send signal to reopen logging infrastructure

    kill -s SIGHUP <nfacctd-proc-id>

Then verify the following:

- Log file was successfully recreated
- Log messages in "output-log-00.log" are also present in the re-created logfile (order of appearence preserved, but there could/will be other logs in between)

# Maintenance server #

## installation ##

The default directory for maintenance install is '/var/maintenance' however, it could be installed anywhere. (in the following the base installation dir used is the default one, if you are using a different one just change the paths)

These maintenances script are designed for OpenBSD 6.7, they came in replacement of the default ones (/etc/[daily,weekly,monthly]) so make sure to deactivate them in the root's crontab

### requirements ###

These scripts require 
 * Python 3.7 (with the default command line '/usr/local/bin/python')
 * 'mysqlclient' python module (`>python3 -m pip install mysqlclient`)
 * a working command `sendmail`
 * a working MySQL server

Many configuration are actually hardcoded but will be externalized in the future

## cron configuration ##

To make the maintenance executed with the right timing, you my nee to add the following lines to the root's crontab:

```
# main maintenance of the server every ten minutes
*/10    *       *       *       *       /usr/local/bin/python3 /var/maintenance/exec.py
# fast maintenance execution every 30 seconds
*       *       *       *       *       /usr/local/bin/python3 /var/maintenance/exec_fast.py
*       *       *       *       *       (sleep 30; /usr/local/bin/python3 /var/maintenance/exec_fast.py)
```

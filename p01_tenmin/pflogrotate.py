#!/usr/bin/env python

import os
crscdir=os.getenv("crscdir","/var/maintenance")
import sys
sys.path.insert(0,crscdir)
from common.maintenance import *

PFLOG= "/var/log/pflog"
FILE = "/var/log/pflog10min"

def pflog_rotate():
    write_log("pflogrotate","executiong pflog rotate")
    lines=system_exec("pkill -ALRM -u root -U root -t - -x pflogd")
    if not os.path.exists(PFLOG):
        return
    if os.stat(PFLOG).st_size <= 24:
        return
    os.rename(PFLOG,FILE)
    lines=system_exec("pkill -HUP -u root -U root -t - -x pflogd")
    lines=system_exec("tcpdump -n -e -s 160 -ttt -r "+FILE+" | logger -t pf -p local0.info")
    os.remove(FILE)

def main():
    pflog_rotate()

if __name__ == "__main__":
    main()
#!/usr/bin/env python
"""
script to rotate lob of pf
"""
from common.maintenance import *

PFLOG = "/var/log/pflog"
FILE = "/var/log/pflog10min"


def pflog_rotate():
    """
    rotate pf log if size get too high
    :return:
    """
    write_log("pflogrotate", "executiong pflog rotate")
    system_exec("pkill -ALRM -u root -U root -t - -x pflogd")
    if not os.path.exists(PFLOG):
        return
    if os.stat(PFLOG).st_size <= 24:
        return
    os.rename(PFLOG, FILE)
    system_exec("pkill -HUP -u root -U root -t - -x pflogd")
    system_exec("tcpdump -n -e -s 160 -ttt -r " + FILE + " | logger -t pf -p local0.info")
    os.remove(FILE)


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    if not dry_run:
        pflog_rotate()


if __name__ == "__main__":
    main()

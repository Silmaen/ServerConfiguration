#!/usr/bin/env python
"""
script to update the syslog
"""
from common.maintenance import *


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    write_log("newsyslog", "runing newsyslog")
    if not dry_run:
        ret, lines = system_exec("/usr/bin/newsyslog", "newsyslog", "newsyslog")
        for line in lines:
            write_log("newsyslog", line)


if __name__ == "__main__":
    main()

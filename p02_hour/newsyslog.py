#!/usr/bin/env python

from common.maintenance import *


def main(dry_run: bool = False):
    write_log("newsyslog", "runing newsyslog")
    if not dry_run:
        lines = system_exec("/usr/bin/newsyslog", "newsyslog", "newsyslog")
        for line in lines:
            write_log("newsyslog", line)


if __name__ == "__main__":
    main()

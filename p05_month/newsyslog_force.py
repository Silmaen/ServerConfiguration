#!/usr/bin/env python

import os
crscdir=os.getenv("crscdir","/var/maintenance")
import sys
sys.path.insert(0,crscdir)
from common.maintenance import *

def newsyslog_forced():
    write_log("monthly","newsyslog forced")
    lines=system_exec("/usr/bin/newsyslog -F")
    if len(lines)!=0:
        # il y a un probleme
        write_log("monthly","problem in newsyslog execution")
        add_mail("Problems in newsyslog execution\n====")
        add_mail("[VERBATIM]")
        for line in lines:
            write_log("monthly",line)
            add_mail(line)
        add_mail("[/VERBATIM]")

def main():
    newsyslog_forced()

if __name__ == "__main__":
    main()
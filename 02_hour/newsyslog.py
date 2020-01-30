#!/usr/bin/env python

import os
crscdir=os.getenv("crscdir","/var/maintenance")
import sys
sys.path.insert(0,crscdir)
from common.maintenance import *

def main():
    write_log("newsyslog","runing newsyslog")
    lines=system_exec("/usr/bin/newsyslog","newsyslog","newsyslog")
    for line in lines:
        write_log("newsyslog",line)

if __name__ == "__main__":
    main()

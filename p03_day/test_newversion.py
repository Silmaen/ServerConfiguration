#!/usr/bin/env python
# - encoding:utf8 -

import os
crscdir=os.getenv("crscdir","/var/maintenance")
import sys
sys.path.insert(0,crscdir)
from common.maintenance import *
from common.trafic_cst import *

baserepository="https://ftp.openbsd.org/pub/OpenBSD/"

def getActualVersion():
    return(system_exec("uname -r")[0])

def incrementVersion(oversion):
    a,b=[int(i) for i in oversion.split(".")]
    if b<9:
        b+=1
    else:
        b=0
        a+=1
    return(str(a)+"."+str(b))

def main():
    write_log("newversion_check","Daily OpenBSD version Check")
    oldversion=getActualVersion()
    newversion=incrementVersion(oldversion).strip()
    urlnew=baserepository+newversion+"/"
    if (existHttpPage(urlnew)):
        write_log("newversion_check","WARNING: new OpenBSD version available!")
        add_mail("WARNING: new OpenBSD version available at: "+urlnew)
    else:
        write_log("newversion_check","no new OpenBSD version available!")
        #write_log("newversion_check"," check at: '"+urlnew+"'")
    urlnew=baserepository+oldversion+"/"
    if (not existHttpPage(urlnew)):
        write_log("newversion_check","WARNING: actual OpenBSD version no more supported")
        add_mail("WARNING: actual OpenBSD version no more supported ")
    else:
        write_log("newversion_check","Actual OpenBSD version still available!")
        #write_log("newversion_check"," check at: '"+urlnew+"'")

if __name__ == "__main__":
    main()

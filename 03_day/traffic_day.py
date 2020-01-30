#!/usr/bin/env python

import os
crscdir=os.getenv("crscdir","/var/maintenance")
import sys
sys.path.insert(0,crscdir)
from common.maintenance import *
from common.trafic_cst import *

def main():
    write_log("trafic_day","Daily Trafic Statistics")
    oldinterf=loadresu()
    for key in Interface.keys():
        if key not in oldinterf.keys():
            continue
        write_log("trafic",Interface[key]+" out:"+bytehuman(oldinterf[key]["out"])+" in:"+bytehuman(oldinterf[key]["in"]))
        add_mail(Interface[key]+" out:"+bytehuman(oldinterf[key]["out"])+" in:"+bytehuman(oldinterf[key]["in"]))
    os.remove(traficfileday)
        
if __name__ == "__main__":
    main()
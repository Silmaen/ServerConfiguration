#!/usr/bin/env python

import os
crscdir=os.getenv("crscdir","/var/maintenance")
import sys
sys.path.insert(0,crscdir)
from common.maintenance import *
from common.trafic_cst import *

def addtodata(oldinterf,rinterf):
    vals={}
    if os.path.exists(traficfileday):
        ft=open(traficfileday,"r")
        ll=ft.readlines()
        ft.close()
        for line in ll:
            item=line.split()
            vals[item[0]]={"out":int(item[1]),"in":int(item[2])}
    ft=open(traficfileday,"w")
    for key in Interface.keys():
        if key not in rinterf.keys():
            continue
        if key not in oldinterf.keys():
            continue
        out=rinterf[key]["out"]-oldinterf[key]["out"]
        if out<0:
            out=rinterf[key]["out"]
        inb=rinterf[key]["in"]-oldinterf[key]["in"]
        if inb<0:
            inb=rinterf[key]["in"]
        if key in vals.keys():
            out+=vals[key]["out"]
            if out<0:
                out=rinterf[key]["out"]
            inb+=vals[key]["in"]
            if inb<0:
                inb=rinterf[key]["in"]
        ft.write(key+" "+str(out)+" "+str(inb)+"\n")
    ft.close()
        
def main():
    write_log("trafic","Trafic computation")
    oldinterf=load()
    rinterf=get_trafic()
    save(rinterf)
    addtodata(oldinterf,rinterf)

if __name__ == "__main__":
    main()
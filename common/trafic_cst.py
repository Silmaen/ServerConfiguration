#!/usr/bin/env python

import os
crscdir=os.getenv("crscdir","/var/maintenance")
import sys
sys.path.insert(0,crscdir)
from common.maintenance import *

traficfile=datadir+"/trafic.txt"
traficfileday=datadir+"/trafic_day.txt"

Interface = {"lo0"    :"Cycling Trafic   ",
             "re0"    :"Internet Trafic  ",
             "bridge0":"Local Trafic     ",
             "nfe0"   :"Local Wire Trafic",
             "athn0"  :"Local Wifi Trafic"}

def lineword(stri):
    # clean space in double:
    r=stri
    r=r.strip()
    re=""
    for i in range(len(r)):
        if (r[i]!=" "):
            re+=r[i]
            continue
        else:
            if i==0:
                continue
            if r[i-1]==" ":
                continue
            re+=r[i]
    return re.split()
    
def get_trafic():
    results=system_exec("netstat -nlib")
    if len(results)<1:
        write_log("trafic","ERROR while retrieving trafic")
    resinterface={}
    for line in results:
        if "<Link>" not in line:
            continue
        word=lineword(line)
        if word[0] not in Interface.keys():
            continue
        out=int(word[-1])
        inb=int(word[-2])
        resinterface[word[0]]={"out":out,"in":inb}
    return resinterface;

def save(rinterf):
    if len(rinterf)==0:
        return
    ft=open(traficfile,"w")
    for key in rinterf.keys():
        ft.write(key+" "+str(rinterf[key]["out"])+" "+str(rinterf[key]["in"])+"\n")
    ft.close()
    
def load():
    res={}
    if not os.path.exists(traficfile):
        return res
    ft=open(traficfile,"r")
    lines=ft.readlines()
    ft.close()
    for line in lines:
        item=line.split()
        res[item[0]]={"out":int(item[1]),"in":int(item[2])}
    return res
    
def loadresu():
    res={}
    if not os.path.exists(traficfileday):
        return res
    ft=open(traficfileday,"r")
    lines=ft.readlines()
    ft.close()
    for line in lines:
        item=line.split()
        res[item[0]]={"out":int(item[1]),"in":int(item[2])}
    return res

def bytehuman( bytes ):
    unit=""
    val=bytes
    if val > 1024:
        val=val/1024.0
        unit="kB"
    if val > 1024:
        val=val/1024.0
        unit="MB"
    if val > 1024:
        val=val/1024.0
        unit="GB"
    if val > 1024:
        val=val/1024.0
        unit="TB"
    if val > 1024:
        val=val/1024.0
        unit="PB"
    return "{:3.1f}".format(val)+unit
    return "{:3.1f}".format(val)+unit
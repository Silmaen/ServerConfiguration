#!/usr/bin/env python

import os
crscdir=os.getenv("crscdir","/var/maintenance")
import sys
sys.path.insert(0,crscdir)
from common.maintenance import *
from common.Connexion_DB import *
import subprocess
import time,datetime
import shutil

def setheaderlines():
    res=[]
    cmd="sysctl -n kern.version"
    lines=system_exec(cmd)
    res.append(lines[0])
    lines=system_exec("uptime")
    res.append(lines[0])
    return res
    
def remove_tmp():
    if not os.path.exists("/tmp"):
        return
    if os.path.islink("/tmp"):
        return
    write_log("daily","Removing scratch and junk files")
    cwd=os.getcwd()
    os.chdir("/tmp")
    list=os.listdir()
    now=time.time()
    for file in list:
        if os.path.isfile(file):
            diff=datetime.date.fromtimestamp(now-os.path.getatime(file))
            if diff.day > 7:
                os.remove(file)
            continue
        if os.path.isdir(file):
            if file in [".",".X11-unix",".ICE-unix","vi.recover"]:
                continue
            diff=datetime.date.fromtimestamp(now-os.path.getmtime(file))
            if diff.day > 1:
                shutil.rmtree(file)
            continue
    os.chdir(cwd)

def purge_account():
    if not os.path.exists("/var/account/acct"):
        return
    write_log("daily","Purging accounting records")
    if os.path.exists("/var/account/acct.2"):
        os.rename("/var/account/acct.2","/var/account/acct.3")
    if os.path.exists("/var/account/acct.1"):
        os.rename("/var/account/acct.1","/var/account/acct.2")
    if os.path.exists("/var/account/acct.0"):
        os.rename("/var/account/acct.0","/var/account/acct.1")
    shutil.copy("/var/account/acct","/var/account/acct.1")

def services():
    lines=system_exec("rcctl ls failed")
    if len(lines)==0:
        # everything is OK!
        return
    write_log("daily","Services that should be running but aren't")
    add_mail("Services that should be running but aren't\n====")
    add_mail("[VERBATIM]")
    for line in lines:
        write_log("daily",line)
        add_mail(line)
    add_mail("[/VERBATIM]")

def disk():
    lines=system_exec("df -hln")
    if len(lines)==0:
        return
    write_log("daily","Disks:")
    add_mail("Disks\n====")
    add_mail("[VERBATIM]")
    for line in lines:
        write_log("daily",line)
        add_mail(line)
    add_mail("[/VERBATIM]")

MySQLParams ={
'host':"localhost",
'user':"robot",
'passwd':"Robot123",
'db':"adiministration"
}

def network():
    lines=system_exec("netstat -ibhn")
    if len(lines)==0:
        return
    write_log("daily","Network:")
    add_mail("Network\n====")
    add_mail("Statistics\n===")
    add_mail("[VERBATIM]")
    for line in lines:
        write_log("daily",line)
        add_mail(line)
    add_mail("[/VERBATIM]")
    #lines=system_exec("netstat -rh")
    #if len(lines)==0:
    #    return
    #write_log("daily","Connected machines:")
    #add_mail("Connected machines\n===")
    #add_mail("[VERBATIM]")
    #IGO=0
    #for line in lines:
    #    if line.startswith("Destination") and IGO==0:
    #        IGO=1
    #        write_log("daily",line)
    #        add_mail(line)
    #        continue
    #    if not "UHLc" in line:
    #        continue
    #    write_log("daily",line)
    #    add_mail(line)
    #add_mail("[/VERBATIM]")
    ending=datetime.datetime.now()
    starting=ending-datetime.timedelta(days=1)
    DB=MyDataBase(MySQLParams,"ClientStatistic")
    if not DB.connexionToDataBase():
        sys.exit(1)
    machineList=DB.getConnexionsBetween(starting,ending)
    lines=DB.printMachineListDuration(machineList)
    write_log("daily","Connected machines:")
    add_mail("Connected machines\n===")
    add_mail("[VERBATIM]")
    IGO=0
    for line in lines:
        write_log("daily",line)
        add_mail(line)
    add_mail("[/VERBATIM]")
    
def main():
    write_log("daily","runing daily procedure")
    #
    hlines=setheaderlines()
    add_mail("DAILY procedure\n=====")
    for hline in hlines:
        add_mail(hline)
    #
    remove_tmp()
    #
    purge_account()
    #
    services()
    #
    disk()
    #
    network()

if __name__ == "__main__":
    main()

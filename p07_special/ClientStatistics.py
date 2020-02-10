#/usr/bin/env python
# encoding: utf-8

import os
crscdir=os.getenv("crscdir","/var/maintenance")
import sys
sys.path.insert(0,crscdir)
from common.maintenance import *
from common.Connexion_DB import *

MySQLParams ={
'host':"localhost",
'user':"robot",
'passwd':"Robot123",
'db':"adiministration"
}

def main():
    write_log("ClientStatistics","Check for client stat")
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

if __name__ == "__main__":
    main()
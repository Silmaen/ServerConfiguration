#!/usr/bin/env python
# -*- coding : utf-8 -*-
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
    #to  lighten th log files... write_log("connexion_table","check connexion table")
    # initilaize data and connect to mysql database
    #DB=MyDataBase(MySQLParams,"connexion_table")
    DB=MyDataBase(MySQLParams,"")
    if not DB.connexionToDataBase():
        sys.exit(1)
    # read database
    if not DB.getActiveMachineList():
        sys.exit(1)
    # look for truely connected machines
    DB.getConnectedMachines()
    # do the comparison between DataBase and measures
    DB.compareMachineList()
    # actualize the server DataBase
    DB.ActualizeDB()
    # close connexion to the server
    DB.connexionClose()

if __name__=="__main__":
    main()

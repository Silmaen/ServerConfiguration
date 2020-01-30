#!/usr/bin/env python
# -*- coding : utf-8 -*-
import os
crscdir=os.getenv("crscdir","/var/maintenance")
import sys
sys.path.insert(0,crscdir)
from common.maintenance import *
import time,datetime
import MySQLdb,copy


class MyDataBase:
    def __init__(self,params,script):
        self.__con=None
        self.__cur=None
        self.params=copy.deepcopy(params)
        self.DBMachines={}
        self.ConnectedMachines={}
        self.ActualizedDBMachines={}
        self.DisonnectedMachines={}
        self.script=script
        
    def connexionToDataBase(self):
        try:
            self.__con= MySQLdb.connect(**self.params)
            if (len(self.script)>0):write_log(self.script,"Connection to data base established!")
            if not self.__con:
                write_log(self.script,"Connexion Error")
                self.__con=None
                self.__cur=None
                return(False)
            self.__cur = self.__con.cursor()
        except MySQLdb.Error as e:
            write_log(self.script,"MySQLdb Error "+str(e.args[0])+": "+str(e.args[1]))
            self.__con=None
            self.__cur=None
            return(False)
        except:
            write_log(self.script,"Unknown Error during connexion!")
            self.__con=None
            self.__cur=None
            return(False)
        return(True)
    
    def connexionClose(self):
        self.__con.close()
        self.__con=None
        self.__cur=None
        self.DBMachines={}
        self.ConnectedMachines={}
        self.ActualizedDBMachines={}
        self.DisonnectedMachines={}
    
    def CustomRequest(self,query):
        try:
            self.__cur.execute(query)
            self.__con.commit()
        except MySQLdb.Error as e:
            write_log(self.script,"MySQLdb Error "+str(e.args[0])+": "+str(e.args[1]))
            return(False,{})
        except:
            write_log(self.script,"Unknown Error for querry: '"+str(query)+"'")
            return(False,{})
        return(True,{r[0]:list(r[1:]) for r in self.__cur.fetchall()})
    
    def getActiveMachineList(self):
        res,rows=self.CustomRequest("SELECT * FROM `ActiveMachine`")
        if not res:
            write_log(self.script,"ERROR retrieving  Machine List")
            return(False)
        self.DBMachines={}
        for row in rows.values():
            self.DBMachines[row[0]]={"IP":row[1],"MAC":row[2],"Start":row[3],"OutMachine":row[4]}
        return(True)

    def getConnectedMachines(self):
        self.ConnectedMachines={}
        lines=system_exec("netstat -rf inet | grep \"UHLc\"")
#        lines2=system_exec("netstat -nrf inet | grep \"UHLc\"")
        for i,l in enumerate(lines):
#            IP=lines2[i].split()[0]
            Name=l.split()[0]
            Mac=l.split()[1]
            IP = get_host_ip(Name)
            if IP == "0.0.0.0":
                continue
            if "link#" in Mac: # ignore delinked connexions
                continue
            out=0
            if "UHLch" in l:
                out=1
            self.ConnectedMachines[Name]={"IP":IP,"MAC":Mac,"Start":datetime.datetime.now(),"OutMachine":out}
    
    def printMachineList(self,dictList):
        print('{:<20}{:<16}{:<18}{:<9}{:<25}{:<25}'.format("Name","IP","MAC","external","starting Time","stoping time"))
        for key,val in dictList.items():
            if "Stop" not in val:
                print('{:<20}{:<16}{:<18}{:<9}{:<25}{:<25}'.format(str(key),str(val["IP"]),str(val["MAC"]),str(val["OutMachine"]),str(val["Start"]).split(".")[0],"connected"))
            else:
                print('{:<20}{:<16}{:<18}{:<9}{:<25}{:<25}'.format(str(key),str(val["IP"]),str(val["MAC"]),str(val["OutMachine"]),str(val["Start"]).split(".")[0],str(val["Stop"]).split(".")[0]))

    def printMachineListDuration(self,dictList):
        lines=[]
        lines.append('{:<20}{:<16}{:<18}{:<9}{:<25}{:<25}'.format("Name","IP","MAC","external","Connexion duration","status"))
        for key,val in dictList.items():
            if "Stop" not in val:
                lines.append('{:<20}{:<16}{:<18}{:<9}{:<25}{:<25}'.format(str(key),str(val["IP"]),str(val["MAC"]),str(val["OutMachine"]),str(val["Duration"]),"connected"))
            else:
                lines.append('{:<20}{:<16}{:<18}{:<9}{:<25}{:<25}'.format(str(key),str(val["IP"]),str(val["MAC"]),str(val["OutMachine"]),str(val["Duration"]),"Disconnected"))
        return(lines)

    def compareMachineList(self):
        self.DisonnectedMachines={}
        self.ActualizedDBMachines={}
        #get the list of deconnected machine:
        for mach,info in self.DBMachines.items():
            if mach not in self.ConnectedMachines.keys():
                self.DisonnectedMachines[mach]=info
                self.DisonnectedMachines[mach]["Stop"]=datetime.datetime.now()
                write_log(self.script,'machine '+str(mach)+' is now disconnected!')
                continue
            newinfo=self.ConnectedMachines[mach]
            if (newinfo['IP']!=info['IP']):
                write_log(self.script,'machine '+str(mach)+' has changed IP')
                self.DisonnectedMachines[mach]=info
                self.DisonnectedMachines[mach]["Stop"]=datetime.datetime.now()
                self.ActualizedDBMachines[mach]=newinfo
                self.ActualizedDBMachines[mach]["tobeupdated"]=1
                continue
            if (newinfo['MAC']!=info['MAC']):
                write_log(self.script,'machine '+str(mach)+' has changed MAC')
                self.DisonnectedMachines[mach]=info
                self.DisonnectedMachines[mach]["Stop"]=datetime.datetime.now()
                self.ActualizedDBMachines[mach]=newinfo
                self.ActualizedDBMachines[mach]["tobeupdated"]=1
                continue
            self.ActualizedDBMachines[mach]=info
        # add new machine to the list
        for mach,info in self.ConnectedMachines.items():
            if mach in self.ActualizedDBMachines.keys():
                continue # already in data base
            write_log(self.script,"New machine in data base: "+str(mach))
            self.ActualizedDBMachines[mach]=info
            self.ActualizedDBMachines[mach]["tobeupdated"]=1
    
    def ActualizeDB(self):
        if not self.__cur:
            write_log(self.script,"ERROR: unable to actialize DB without proper connection")
            return(False)
        # ajout d'entrées dans les archives
        for mach,info in self.DisonnectedMachines.items():
            #INSERT INTO `ConnexionArchive` (`ID`, `MachineName`, `IP`, `MAC Address`, `ConnexionStart`, `ConnexionEnd`, `outMachine`) VALUES (NULL, 'totocoincoin', '192.168.2.1', '00:23:54:94:13:fd', '2019-01-01 00:00:00', '2019-01-03 00:00:00', '0');
            cmd="INSERT INTO `ConnexionArchive` (`ID`, `MachineName`, `IP`, `MAC Address`, `ConnexionStart`, `ConnexionEnd`, `outMachine`) VALUES (NULL"
            cmd+=", '"+str(mach)+"'"
            cmd+=", '"+str(info["IP"])+"'"
            cmd+=", '"+str(info["MAC"])+"'"
            cmd+=", '"+str(info["Start"]).split(".")[0]+"'"
            cmd+=", '"+str(info["Stop"]).split(".")[0]+"'"
            cmd+=", '"+str(info["OutMachine"])+"'"
            cmd+=");"
            #print(cmd)
            res,_=self.CustomRequest(cmd)
            if not res:
                write_log(self.script,"ERROR adding entry to database, cmd="+cmd)
                return(False)
            cmd="DELETE FROM `ActiveMachine` WHERE `ActiveMachine`.`MachineName` = '"+mach+"'"
            res,_=self.CustomRequest(cmd)
            if not res:
                write_log(self.script,"ERROR removing entry to database, cmd="+cmd)
                return(False)
        #mise à jour de la base active
        for mach,info in self.ActualizedDBMachines.items():
            if "tobeupdated" not in info: 
                continue
            if mach in self.DBMachines:
                # UPDATE `ActiveMachine` SET `MachineName` = 'totoconcon', `IP` = '127.0.0.14', `MAC Address` = '25:25:25:25:25:24', `ConnexionStart` = '2019-01-16 13:33:59', `OutMachine` = '7' WHERE `ActiveMachine`.`ID` = 1;
                cmd="UPDATE `ActiveMachine` SET"
                cmd+=" `IP` = '"+str(info["IP"])+"'"
                cmd+=", `MAC Address` = '"+str(info["MAC"])+"'"
                cmd+=", `ConnexionStart` = '"+str(info["Start"]).split(".")[0]+"'"
                cmd+=", `OutMachine` = '"+str(info["OutMachine"])+"'"
                cmd+=" WHERE `ActiveMachine`.`MachineName` = '"+str(mach)+"';"
                #print(cmd)
                res,_=self.CustomRequest(cmd)
                if not res:
                    write_log(self.script,"ERROR updating entry in database, cmd="+cmd)
                    return(False)
            else:
                # INSERT ...
                cmd="INSERT INTO `ActiveMachine` (`ID`, `MachineName`, `IP`, `MAC Address`, `ConnexionStart`, `OutMachine`) VALUES (NULL"
                cmd+=", '"+str(mach)+"'"
                cmd+=", '"+str(info["IP"])+"'"
                cmd+=", '"+str(info["MAC"])+"'"
                cmd+=", '"+str(info["Start"]).split(".")[0]+"'"
                cmd+=", '"+str(info["OutMachine"])+"'"
                cmd+=");"
                #print(cmd)
                res,_=self.CustomRequest(cmd)
                if not res:
                    write_log(self.script,"ERROR adding entry to database, cmd="+cmd)
                    return(False)
        return(True)

    def getConnexionsBetween(self,TimeStart,TimeStop):
        machineList={}
        # check connected machines
        self.getActiveMachineList()
        for mach,info in self.DBMachines.items():
            machineList[mach]=copy.deepcopy(info)
            machineList[mach]["Duration"]=datetime.datetime.now()-machineList[mach]["Start"]
        # check connexion history
        cmd="SELECT * FROM `ConnexionArchive` WHERE `ConnexionEnd` BETWEEN '"+str(TimeStart)+"' AND '"+str(TimeStop)+"'"
        res,rows=self.CustomRequest(cmd)
        for row in rows.values():
            if row[0] in machineList:
                machineList[mach]["Duration"]+=row[4]-row[3]
                continue
            machineList[row[0]]={"IP":row[1],"MAC":row[2],"Start":row[3],"Stop":row[4],"OutMachine":row[5]}
            machineList[row[0]]["Duration"]=row[4]-row[3]
        return(machineList)

#!/usr/bin/env python
# -*- coding : utf-8 -*-
from .maintenance import *
import datetime
import MySQLdb
import copy


def print_machine_list(dict_list):
    print('{:<20}{:<16}{:<18}{:<9}{:<25}{:<25}'.format("Name", "IP", "MAC", "external", "starting Time",
                                                       "stoping time"))
    for key, val in dict_list.items():
        if "Stop" not in val:
            print('{:<20}{:<16}{:<18}{:<9}{:<25}{:<25}'.format(str(key), str(val["IP"]), str(val["MAC"]),
                                                               str(val["OutMachine"]),
                                                               str(val["Start"]).split(".")[0], "connected"))
        else:
            print('{:<20}{:<16}{:<18}{:<9}{:<25}{:<25}'.format(str(key), str(val["IP"]), str(val["MAC"]),
                                                               str(val["OutMachine"]),
                                                               str(val["Start"]).split(".")[0],
                                                               str(val["Stop"]).split(".")[0]))


def print_machine_list_duration(dict_list):
    lines = ['{:<20}{:<16}{:<18}{:<9}{:<25}{:<25}'.format("Name", "IP", "MAC", "external", "Connexion duration",
                                                          "status")]
    for key, val in dict_list.items():
        if "Stop" not in val:
            lines.append('{:<20}{:<16}{:<18}{:<9}{:<25}{:<25}'.format(str(key), str(val["IP"]), str(val["MAC"]),
                                                                      str(val["OutMachine"]), str(val["Duration"]),
                                                                      "connected"))
        else:
            lines.append('{:<20}{:<16}{:<18}{:<9}{:<25}{:<25}'.format(str(key), str(val["IP"]), str(val["MAC"]),
                                                                      str(val["OutMachine"]), str(val["Duration"]),
                                                                      "Disconnected"))
    return lines


class MyDataBase:
    def __init__(self, params, script):
        self.__con = None
        self.__cur = None
        self.params = copy.deepcopy(params)
        self.DBMachines = {}
        self.ConnectedMachines = {}
        self.ActualizedDBMachines = {}
        self.DisonnectedMachines = {}
        if script == "":
            self.script = "MySQL Connector"
        else:
            self.script = script

    def db_connexion(self):
        try:
            self.__con = MySQLdb.connect(**self.params)
            #if len(self.script) > 0:
            #    write_log(self.script, "Connection to data base established!")
            if not self.__con:
                write_log(self.script, "Connexion Error")
                self.__con = None
                self.__cur = None
                return False
            self.__cur = self.__con.cursor()
        except MySQLdb.Error as e:
            write_log(self.script, "MySQLdb Error " + str(e.args[0]) + ": " + str(e.args[1]))
            self.__con = None
            self.__cur = None
            return False
        except:
            write_log(self.script, "Unknown Error during connexion!")
            self.__con = None
            self.__cur = None
            return False
        return True

    def close_connexion(self):
        self.__con.close()
        self.__con = None
        self.__cur = None
        self.DBMachines = {}
        self.ConnectedMachines = {}
        self.ActualizedDBMachines = {}
        self.DisonnectedMachines = {}

    def db_request(self, query):
        try:
            self.__cur.execute(query)
            self.__con.commit()
        except MySQLdb.Error as e:
            write_log(self.script, "MySQLdb Error " + str(e.args[0]) + ": " + str(e.args[1]))
            return False, {}
        except:
            write_log(self.script, "Unknown Error for querry: '" + str(query) + "'")
            return False, {}
        return True, {r[0]: list(r[1:]) for r in self.__cur.fetchall()}

    def get_active_machine_list(self):
        res, rows = self.db_request("SELECT * FROM `ActiveMachine`")
        if not res:
            write_log(self.script, "ERROR retrieving  Machine List")
            return False
        self.DBMachines = {}
        for row in rows.values():
            self.DBMachines[row[0]] = {"IP": row[1], "MAC": row[2], "Start": row[3], "OutMachine": row[4]}
        return True

    def get_connected_machines(self):
        self.ConnectedMachines = {}
        lines = system_exec('netstat -rf inet | grep "UHLc"')
        for i, l in enumerate(lines):
            #            IP=lines2[i].split()[0]
            name = l.split()[0]
            mac = l.split()[1]
            ip = get_host_ip(name)
            if ip == "0.0.0.0":
                continue
            if "link#" in mac:  # ignore unlinked connexions
                continue
            out = 0
            if "UHLch" in l:
                out = 1
            self.ConnectedMachines[name] = {"IP": ip, "MAC": mac, "Start": datetime.datetime.now(), "OutMachine": out}

    def compare_machine_list(self):
        self.DisonnectedMachines = {}
        self.ActualizedDBMachines = {}
        # get the list of disconnected machines:
        for mach, info in self.DBMachines.items():
            if mach not in self.ConnectedMachines.keys():
                self.DisonnectedMachines[mach] = info
                self.DisonnectedMachines[mach]["Stop"] = datetime.datetime.now()
                write_log(self.script, 'machine ' + str(mach) + ' is now disconnected!')
                continue
            new_info = self.ConnectedMachines[mach]
            if new_info['IP'] != info['IP']:
                write_log(self.script, 'machine ' + str(mach) + ' has changed IP')
                self.DisonnectedMachines[mach] = info
                self.DisonnectedMachines[mach]["Stop"] = datetime.datetime.now()
                self.ActualizedDBMachines[mach] = new_info
                self.ActualizedDBMachines[mach]["tobeupdated"] = 1
                continue
            if new_info['MAC'] != info['MAC']:
                write_log(self.script, 'machine ' + str(mach) + ' has changed MAC')
                self.DisonnectedMachines[mach] = info
                self.DisonnectedMachines[mach]["Stop"] = datetime.datetime.now()
                self.ActualizedDBMachines[mach] = new_info
                self.ActualizedDBMachines[mach]["tobeupdated"] = 1
                continue
            self.ActualizedDBMachines[mach] = info
        # add new machine to the list
        for mach, info in self.ConnectedMachines.items():
            if mach in self.ActualizedDBMachines.keys():
                continue  # already in data base
            write_log(self.script, "New machine in data base: " + str(mach))
            self.ActualizedDBMachines[mach] = info
            self.ActualizedDBMachines[mach]["tobeupdated"] = 1

    def bd_actualize(self):
        if not self.__cur:
            write_log(self.script, "ERROR: unable to actialize DB without proper connection")
            return False
        # add entry in archives
        for mach, info in self.DisonnectedMachines.items():
            # INSERT INTO `ConnexionArchive` (`ID`, `MachineName`, `IP`, `MAC Address`, `ConnexionStart`,
            # `ConnexionEnd`, `outMachine`) VALUES (NULL, 'totocoincoin', '192.168.2.1', '00:23:54:94:13:fd',
            # '2019-01-01 00:00:00', '2019-01-03 00:00:00', '0');
            cmd = "INSERT INTO `ConnexionArchive` (`ID`, `MachineName`, `IP`, `MAC Address`, `ConnexionStart`, " \
                  "`ConnexionEnd`, `outMachine`) VALUES (NULL "
            cmd += ", '" + str(mach) + "'"
            cmd += ", '" + str(info["IP"]) + "'"
            cmd += ", '" + str(info["MAC"]) + "'"
            cmd += ", '" + str(info["Start"]).split(".")[0] + "'"
            cmd += ", '" + str(info["Stop"]).split(".")[0] + "'"
            cmd += ", '" + str(info["OutMachine"]) + "'"
            cmd += ");"
            # print(cmd)
            res, _ = self.db_request(cmd)
            if not res:
                write_log(self.script, "ERROR adding entry to database, cmd=" + cmd)
                return False
            cmd = "DELETE FROM `ActiveMachine` WHERE `ActiveMachine`.`MachineName` = '" + mach + "'"
            res, _ = self.db_request(cmd)
            if not res:
                write_log(self.script, "ERROR removing entry to database, cmd=" + cmd)
                return False
        # update active database
        for mach, info in self.ActualizedDBMachines.items():
            if "tobeupdated" not in info:
                continue
            if mach in self.DBMachines:
                # UPDATE `ActiveMachine` SET `MachineName` = 'totoconcon', `IP` = '127.0.0.14', `MAC Address` =
                # '25:25:25:25:25:24', `ConnexionStart` = '2019-01-16 13:33:59', `OutMachine` = '7' WHERE
                # `ActiveMachine`.`ID` = 1;
                cmd = "UPDATE `ActiveMachine` SET"
                cmd += " `IP` = '" + str(info["IP"]) + "'"
                cmd += ", `MAC Address` = '" + str(info["MAC"]) + "'"
                cmd += ", `ConnexionStart` = '" + str(info["Start"]).split(".")[0] + "'"
                cmd += ", `OutMachine` = '" + str(info["OutMachine"]) + "'"
                cmd += " WHERE `ActiveMachine`.`MachineName` = '" + str(mach) + "';"
                # print(cmd)
                res, _ = self.db_request(cmd)
                if not res:
                    write_log(self.script, "ERROR updating entry in database, cmd=" + cmd)
                    return False
            else:
                # INSERT ...
                cmd = "INSERT INTO `ActiveMachine` (`ID`, `MachineName`, `IP`, `MAC Address`, `ConnexionStart`, " \
                      "`OutMachine`) VALUES (NULL "
                cmd += ", '" + str(mach) + "'"
                cmd += ", '" + str(info["IP"]) + "'"
                cmd += ", '" + str(info["MAC"]) + "'"
                cmd += ", '" + str(info["Start"]).split(".")[0] + "'"
                cmd += ", '" + str(info["OutMachine"]) + "'"
                cmd += ");"
                # print(cmd)
                res, _ = self.db_request(cmd)
                if not res:
                    write_log(self.script, "ERROR adding entry to database, cmd=" + cmd)
                    return False
        return True

    def get_connexions_between(self, time_start, time_stop):
        machine_list = {}
        # check connected machines
        self.get_active_machine_list()
        for mach, info in self.DBMachines.items():
            machine_list[mach] = copy.deepcopy(info)
            machine_list[mach]["Duration"] = datetime.datetime.now() - machine_list[mach]["Start"]
        # check connexion history
        cmd = "SELECT * FROM `ConnexionArchive` WHERE `ConnexionEnd` BETWEEN '" + str(time_start) + "' AND '" + str(
            time_stop) + "'"
        res, rows = self.db_request(cmd)
        for row in rows.values():
            if row[0] in machine_list:
                machine_list[mach]["Duration"] += row[4] - row[3]
                continue
            machine_list[row[0]] = {"IP": row[1], "MAC": row[2], "Start": row[3], "Stop": row[4], "OutMachine": row[5]}
            machine_list[row[0]]["Duration"] = row[4] - row[3]
        return machine_list

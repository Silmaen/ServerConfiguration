#!/usr/bin/env python
# -*- coding : utf-8 -*-
"""
script for the maintenance of the list of connected machines, update data base and DNS zones
"""
from common.machine import get_active_machine_db, get_connected_machines, mac_compare
'''
from common.Connexion_DB import *

MySQLParams = {
    'host': "localhost",
    'user': "robot",
    'passwd': "Robot123",
    'db': "adiministration"
}


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    # to  lighten th log files... logger.log("connexion_table","check connexion table")
    # initialize data and connect to mysql database
    db = MyDataBase(MySQLParams, "")
    if not db.db_connexion():
        logger.log("connexion_table", "No connexion to MySQL database!")
        return
    # read database
    if not db.get_active_machine_list():
        logger.log("connexion_table", "MySQL database has no Active machine list")
        return
    # look for true connected machines
    db.get_connected_machines()
    # do the comparison between DataBase and measures
    db.compare_machine_list()
    # actualize the server DataBase
    if not dry_run:
        db.bd_actualize()
    # close connexion to the server
    db.close_connexion()
'''


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    machine_list_db = get_active_machine_db()
    machine_list_con = get_connected_machines()
    machines = []
    for m1 in machine_list_con:
        m = None
        for m2 in machine_list_db:
            if not mac_compare(m1.mac, m2.mac):
                continue
            m = m2
            m.inDB = True
            break
        if not m:
            # pas dans la base: probablement une nouvelle machine
            machines.append(m1)
            continue


if __name__ == "__main__":
    main()

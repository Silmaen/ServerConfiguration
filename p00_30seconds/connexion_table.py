#!/usr/bin/env python
# -*- coding : utf-8 -*-
from common.Connexion_DB import *

MySQLParams = {
    'host': "localhost",
    'user': "robot",
    'passwd': "Robot123",
    'db': "administration"
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


if __name__ == "__main__":
    main()

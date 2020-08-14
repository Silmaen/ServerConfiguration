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

    from common.CodeTimer import CodeTimer
    ct = CodeTimer("connexion_table")
    db = MyDataBase(MySQLParams, "")
    if not db.db_connexion():
        logger.log_error("connexion_table", "No connexion to MySQL database!")
        return
    logger.log("connexion_table", ct.format_current("db connexion"))
    # read database
    if not db.get_active_machine_list():
        logger.log_error("connexion_table", "MySQL database has no Active machine list")
        return
    logger.log("connexion_table", ct.format_current("get active machine"))
    # look for true connected machines
    db.get_connected_machines()
    logger.log("connexion_table", ct.format_current("get connected machine"))
    # do the comparison between DataBase and measures
    db.compare_machine_list()
    logger.log("connexion_table", ct.format_current("compare machine list"))
    # actualize the server DataBase
    if not dry_run:
        db.bd_actualize()
        logger.log("connexion_table", ct.format_current("actualize db"))
    # close connexion to the server
    db.close_connexion()
    logger.log("connexion_table", ct.format_current("closing"))
    logger.log("connexion_table", ct.format_long())


if __name__ == "__main__":
    main()

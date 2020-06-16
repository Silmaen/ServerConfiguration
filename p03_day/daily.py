#!/usr/bin/env python
"""
the daily procedure (coming from OpenBSD)
"""
from common.Connexion_DB import *
import time
import datetime
import shutil


def setheaderlines():
    """
    get information about kernel version and uptime
    :return: lines to be printed in mail
    """
    res = []
    cmd = "sysctl -n kern.version"
    ret, lines = system_exec(cmd)
    res.append(lines[0])
    ret, lines = system_exec("uptime")
    res.append(lines[0])
    return res


def remove_tmp():
    """
    clean the /tmp folder
    :return:
    """
    if not os.path.exists("/tmp"):
        return
    if os.path.islink("/tmp"):
        return
    logger.log("daily", "Removing scratch and junk files")
    cwd = os.getcwd()
    os.chdir("/tmp")
    list_dir = os.listdir()
    now = time.time()
    for file in list_dir:
        if os.path.isfile(file):
            diff = datetime.date.fromtimestamp(now - os.path.getatime(file))
            if diff.day > 7:
                os.remove(file)
            continue
        if os.path.isdir(file):
            if file in [".", ".X11-unix", ".ICE-unix", "vi.recover"]:
                continue
            diff = datetime.date.fromtimestamp(now - os.path.getmtime(file))
            if diff.day > 1:
                shutil.rmtree(file)
            continue
    os.chdir(cwd)


def purge_account():
    """
    purge the account data
    :return:
    """
    if not os.path.exists("/var/account/acct"):
        return
    logger.log("daily", "Purging accounting records")
    if os.path.exists("/var/account/acct.2"):
        os.rename("/var/account/acct.2", "/var/account/acct.3")
    if os.path.exists("/var/account/acct.1"):
        os.rename("/var/account/acct.1", "/var/account/acct.2")
    if os.path.exists("/var/account/acct.0"):
        os.rename("/var/account/acct.0", "/var/account/acct.1")
    shutil.copy("/var/account/acct", "/var/account/acct.1")


def services():
    """
    check for service that are not runin
    :return:
    """
    ret, lines = system_exec("rcctl ls failed")
    if len(lines) == 0:
        # everything is OK!
        return
    logger.log("daily", "Services that should be running but aren't")
    add_mail("Services that should be running but aren't\n====")
    add_mail("[VERBATIM]")
    for line in lines:
        logger.log("daily", line)
        add_mail(line)
    add_mail("[/VERBATIM]")


def disk():
    """
    check disk space
    :return:
    """
    ret, lines = system_exec("df -hl")
    if len(lines) == 0:
        return
    logger.log("daily", "Disks:")
    add_mail("Disks\n====")
    add_mail("[VERBATIM]")
    for line in lines:
        logger.log("daily", line)
        add_mail(line)
    add_mail("[/VERBATIM]")


MySQLParams = {
    'host': "localhost",
    'user': "robot",
    'passwd': "Robot123",
    'db': "administration"
}


def network():
    """
    compute network statistics
    :return:
    """
    ret, lines = system_exec("netstat -ibhn")
    if len(lines) == 0:
        return
    logger.log("daily", "Network:")
    add_mail("Network\n====")
    add_mail("Statistics\n===")
    add_mail("[VERBATIM]")
    for line in lines:
        logger.log("daily", line)
        add_mail(line)
    add_mail("[/VERBATIM]")
    ending = datetime.datetime.now()
    starting = ending - datetime.timedelta(days=1)
    DB = MyDataBase(MySQLParams, "ClientStatistic")
    if not DB.db_connexion():
        logger.log("ClientStatistics", "Unable to get the database")
        return
    machine_list = DB.get_connexions_between(starting, ending)
    lines = print_machine_list_duration(machine_list)
    logger.log("daily", "Connected machines:")
    add_mail("Connected machines\n===")
    add_mail("[VERBATIM]")
    for line in lines:
        logger.log("daily", line)
        add_mail(line)
    add_mail("[/VERBATIM]")


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    logger.log("daily", "runing daily procedure")
    #
    hlines = setheaderlines()
    add_mail("DAILY procedure\n=====")
    for hline in hlines:
        add_mail(hline)
    #
    if not dry_run:
        remove_tmp()
    #
    if not dry_run:
        purge_account()
    #
    services()
    #
    disk()
    #
    network()


if __name__ == "__main__":
    main()

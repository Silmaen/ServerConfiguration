#!/usr/bin/env python
"""
the daily procedure (coming from OpenBSD)
"""
import datetime
import shutil
import time

from common.Connexion_DB import *
from common.LoggingSystem import get_error_list
from common.MailingSystem import add_paragraph_with_items, add_paragraph, add_paragraph_with_array, add_mail_line, add_paragraph_with_lines


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
    logger.log("daily", "Services that should be running but aren't\n" + "\n".join(lines))
    add_paragraph_with_items("Services that should be running but aren't", lines=lines)


def disk():
    """
    check disk space
    :return:
    """
    ret, lines = system_exec("df -hl")
    if len(lines) == 0:
        return
    logger.log("daily", "Disks:\n" + "\n".join(lines))
    add_paragraph_with_items("Disks", lines=lines)


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
    logger.log("daily", "\n".join(lines))
    add_mail_line("## Network ##")
    add_paragraph_with_lines("Statistics", 3, lines=lines)
    ending = datetime.datetime.now()
    starting = ending - datetime.timedelta(days=1)
    DB = MyDataBase(MySQLParams, "ClientStatistic")
    if not DB.db_connexion():
        logger.log("ClientStatistics", "Unable to get the database")
        return
    machine_list = DB.get_connexions_between(starting, ending)
    lines = print_machine_list_duration(machine_list)
    logger.log("daily", "Connected machines:")
    logger.log("daily", "\n".join(lines))
    add_paragraph_with_lines("Connected machines", 3, lines=lines)


def check_daily_errors():
    """
    check for error in database
    """
    err_list = get_error_list()
    if len(err_list) == 0:
        add_paragraph("Error Status", message="Everything is good!")
    else:
        errors_md = []
        for err in err_list:
            errors_md.append(err.to_md_array())
        add_paragraph_with_array("Too Many Errors in one Hour", col_titles=["time", "who", "message"], rows=errors_md)


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    logger.log("daily", "runing daily procedure")
    #
    hlines = setheaderlines()
    add_paragraph_with_lines("DAILY procedure", 3, lines=hlines)
    #
    if not dry_run:
        remove_tmp()
    #
    if not dry_run:
        purge_account()
    #
    services()
    #
    check_daily_errors()
    #
    disk()
    #
    network()


if __name__ == "__main__":
    main()

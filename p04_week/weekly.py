#!/usr/bin/env python

from common.maintenance import *


def locate_database():
    # /usr/libexec/locate.updatedb
    write_log("weekly", "Updating locate database")
    lines = system_exec("/usr/libexec/locate.updatedb")
    if len(lines) != 0:
        # houston, we got a problem
        write_log("weekly", "problem in locate database update")
        add_mail("Problems in locate database reconstruction\n====")
        add_mail("[VERBATIM]")
        for line in lines:
            write_log("weekly", line)
            add_mail(line)
        add_mail("[/VERBATIM]")


def check_packages():
    # now check packages
    lines = system_exec("pkg_check -xq")
    ok = True
    for line in lines:
        if "ok" not in line:
            ok = False
            break
    if not ok:
        # houston, we got a problem
        write_log("weekly", "problem in packages")
        add_mail("Problems in packages\n====")
        add_mail("[VERBATIM]")
        for line in lines:
            write_log("weekly", line)
            add_mail(line)
        add_mail("[/VERBATIM]")


def whatis_database():
    # /usr/sbin/makewhatis
    write_log("weekly", "whatis database update")
    lines = system_exec("/usr/sbin/makewhatis")
    if len(lines) != 0:
        # il y a un probleme
        write_log("weekly", "problem in whatis database update")
        add_mail("Problems in whatis database reconstruction\n====")
        add_mail("[VERBATIM]")
        for line in lines:
            write_log("weekly", line)
            add_mail(line)
        add_mail("[/VERBATIM]")


def login_account():
    # ac -p | sort -nr -k 2
    write_log("weekly", "login time statistics")
    lines = system_exec("ac -p | sort -nr -k 2")
    add_mail("Login statistics\n====")
    add_mail("[VERBATIM]")
    for line in lines:
        write_log("weekly", line)
        add_mail(line)
    add_mail("[/VERBATIM]")


def main(dry_run: bool = False):
    write_log("weekly", "runing weekly procedure")
    #
    add_mail("WEEKLY procedure\n=====")
    #
    if not dry_run:
        locate_database()
    #
    check_packages()
    #
    if not dry_run:
        whatis_database()
    #
    login_account()
    #
    #


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
weekly procedures (based on OpenBSD ones)
"""
from common.maintenance import logger, system_exec
from common.MailingSystem import add_paragraph_with_lines, add_mail_line


def locate_database():
    """
    update the locate database
    :return:
    """
    # /usr/libexec/locate.updatedb
    logger.log("weekly", "Updating locate database")
    ret, lines = system_exec("/usr/libexec/locate.updatedb")
    if len(lines) != 0:
        # houston, we got a problem
        logger.log_error("weekly", "problem in locate database update\n" + "\n".join(lines))
        add_paragraph_with_lines("locate_database", 3, pre_message=["Problems in locate database reconstruction"],
                                 lines=lines)


def check_packages():
    """
    check the package installation
    :return:
    """
    # now check packages
    ret, lines = system_exec("pkg_check -xq")
    ok = True
    for line in lines:
        if "ok" not in line:
            ok = False
            break
    if not ok:
        # houston, we got a problem
        logger.log_error("weekly", "problem in packages\n" + "\n".join(lines))
        add_paragraph_with_lines("check_packages", 3, pre_message=["problem in packages"],
                                 lines=lines)


def whatis_database():
    """
    update the whatis database
    :return:
    """
    # /usr/sbin/makewhatis
    logger.log("weekly", "whatis database update")
    ret, lines = system_exec("/usr/sbin/makewhatis")
    if len(lines) != 0:
        # il y a un probleme
        logger.log_error("weekly", "problem in whatis database update\n" + "\n".join(lines))
        add_paragraph_with_lines("whatis_database", 3, pre_message=["problem in whatis database update"],
                                 lines=lines)


def login_account():
    """
    get login statistics (not really working)
    :return:
    """
    # ac -p | sort -nr -k 2
    ret, lines = system_exec("ac -p | sort -nr -k 2")
    logger.log("weekly", "login time statistics\n" + "\n".join(lines))
    add_paragraph_with_lines("Login statistic", 3, lines=lines)


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    logger.log("weekly", "running weekly procedure")
    #
    add_mail_line("##WEEKLY procedure##")
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

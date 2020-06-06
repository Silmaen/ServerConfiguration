#!/usr/bin/env python
# - encoding:utf8 -
"""
scrit for testing the possibility to upgrade the system
"""

from common.trafic_cst import *

base_repository = "https://ftp.openbsd.org/pub/OpenBSD/"


def get_actual_version():
    """
    retreave te actual version number
    :return: version
    """
    ret, version = system_exec("uname -r")
    version = version[0]
    if "." not in version:
        return "0.0"
    return ".".join(version.split(".")[0:2])


def increment_version(old_version):
    """
    determine the next version number
    :param old_version: the starting version
    :return: the version number incremented
    """
    a, b = [int(i) for i in old_version.split(".")]
    if b < 9:
        b += 1
    else:
        b = 0
        a += 1
    return str(a) + "." + str(b)


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    logger.log("newversion_check", "Daily OpenBSD version Check" + ["", " dry"][dry_run])
    old_version = get_actual_version()
    new_version = increment_version(old_version).strip()
    url_new = base_repository + new_version + "/"
    if exist_http_page(url_new):
        logger.log("newversion_check", "WARNING: new OpenBSD version available!")
        add_mail("WARNING: new OpenBSD version available at: " + url_new)
    else:
        logger.log("newversion_check", "no new OpenBSD version available!")
        # logger.log("newversion_check"," check at: '"+urlnew+"'")
    url_new = base_repository + old_version + "/"
    if not exist_http_page(url_new):
        logger.log("newversion_check", "WARNING: actual OpenBSD version no more supported")
        add_mail("WARNING: actual OpenBSD version no more supported ")
    else:
        logger.log("newversion_check", "Actual OpenBSD version still available!")


if __name__ == "__main__":
    main()

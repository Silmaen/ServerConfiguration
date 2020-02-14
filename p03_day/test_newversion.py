#!/usr/bin/env python
# - encoding:utf8 -

from common.trafic_cst import *

base_repository = "https://ftp.openbsd.org/pub/OpenBSD/"


def get_actual_version():
    version = system_exec("uname -r")[0]
    if "." not in version:
        return "0.0"
    return ".".join(version.split(".")[0:2])


def increment_version(old_version):
    a, b = [int(i) for i in old_version.split(".")]
    if b < 9:
        b += 1
    else:
        b = 0
        a += 1
    return str(a) + "." + str(b)


def main(dry_run: bool = False):
    write_log("newversion_check", "Daily OpenBSD version Check" + ["", " dry"][dry_run])
    old_version = get_actual_version()
    new_version = increment_version(old_version).strip()
    url_new = base_repository + new_version + "/"
    if exist_http_page(url_new):
        write_log("newversion_check", "WARNING: new OpenBSD version available!")
        add_mail("WARNING: new OpenBSD version available at: " + url_new)
    else:
        write_log("newversion_check", "no new OpenBSD version available!")
        # write_log("newversion_check"," check at: '"+urlnew+"'")
    url_new = base_repository + old_version + "/"
    if not exist_http_page(url_new):
        write_log("newversion_check", "WARNING: actual OpenBSD version no more supported")
        add_mail("WARNING: actual OpenBSD version no more supported ")
    else:
        write_log("newversion_check", "Actual OpenBSD version still available!")


if __name__ == "__main__":
    main()

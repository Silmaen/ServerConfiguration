#!/usr/bin/env python

from common.trafic_cst import *


def main(dry_run: bool = False):
    write_log("trafic_day", "Daily Trafic Statistics")
    oldinterf = load_result()
    for key in Interface.keys():
        if key not in oldinterf.keys():
            continue
        write_log("trafic", Interface[key] + " out:" + byte_human(oldinterf[key]["out"]) + " in:" + byte_human(
            oldinterf[key]["in"]))
        add_mail(
            Interface[key] + " out:" + byte_human(oldinterf[key]["out"]) + " in:" + byte_human(oldinterf[key]["in"]))
    if not dry_run:
        os.remove(traffic_file_day)


if __name__ == "__main__":
    main()

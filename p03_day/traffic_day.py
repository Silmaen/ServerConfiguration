#!/usr/bin/env python
"""
script to determine the daily network trafic
"""
from common.trafic_cst import *
from common.MailingSystem import add_paragraph_with_array


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    logger.log("trafic_day", "Daily Trafic Statistics")
    oldinterf = load_result()
    interf = []
    for key in Interface.keys():
        if key not in oldinterf.keys():
            continue
        logger.log("trafic", Interface[key] + " out:" + byte_human(oldinterf[key]["out"]) + " in:" + byte_human(
            oldinterf[key]["in"]))
        interf.append([Interface[key], byte_human(oldinterf[key]["out"]), byte_human(oldinterf[key]["in"])])
    add_paragraph_with_array("Daily Trafic Statistics", col_titles=["interface", "in", "ont"], rows=interf)
    if not dry_run:
        os.remove(traffic_file_day)


if __name__ == "__main__":
    main()

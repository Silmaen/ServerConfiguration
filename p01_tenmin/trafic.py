#!/usr/bin/env python
"""
script for trafic computation
"""
from common.trafic_cst import *


def add_to_data(old_interface, r_interface):
    """
    compute trafic and update database
    :param old_interface:
    :param r_interface:
    :return:
    """
    values = {}
    if os.path.exists(traffic_file_day):
        ft = open(traffic_file_day)
        ll = ft.readlines()
        ft.close()
        for line in ll:
            item = line.split()
            values[item[0]] = {"out": int(item[1]), "in": int(item[2])}
    ft = open(traffic_file_day, "w")
    for key in Interface.keys():
        if key not in r_interface.keys():
            continue
        if key not in old_interface.keys():
            continue
        out = r_interface[key]["out"] - old_interface[key]["out"]
        if out < 0:
            out = r_interface[key]["out"]
        inb = r_interface[key]["in"] - old_interface[key]["in"]
        if inb < 0:
            inb = r_interface[key]["in"]
        if key in values.keys():
            out += values[key]["out"]
            if out < 0:
                out = r_interface[key]["out"]
            inb += values[key]["in"]
            if inb < 0:
                inb = r_interface[key]["in"]
        ft.write(key + " " + str(out) + " " + str(inb) + "\n")
    ft.close()


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    logger.log("trafic", "Traffic computation")
    old_interface = load()
    r_interface = get_traffic()
    if not dry_run:
        save(r_interface)
        add_to_data(old_interface, r_interface)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
trafic constants
"""
import os
from common.AllDefaultParameters import *
from common.maintenance import system_exec, logger

traffic_file = os.path.join(data_dir, "traffic.txt")
traffic_file_day = os.path.join(data_dir, "traffic_day.txt")

Interface = {"lo0": "Cycling Traffic   ",
             "re0": "Internet Traffic  ",
             "bridge0": "Local Traffic     ",
             "nfe0": "Local Wire Traffic",
             "athn0": "Local Wifi Traffic"}


def line_word(string_to_split):
    # clean space in double:
    r = string_to_split
    r = r.strip()
    re = ""
    for i in range(len(r)):
        if r[i] != " ":
            re += r[i]
            continue
        else:
            if i == 0:
                continue
            if r[i - 1] == " ":
                continue
            re += r[i]
    return re.split()


def get_traffic():
    ret, results = system_exec("netstat -nlib")
    if len(results) < 1:
        logger.log_error("get_traffic", "ERROR while retrieving traffic")
    res_interface = {}
    for line in results:
        if "<Link>" not in line:
            continue
        word = line_word(line)
        if word[0] not in Interface.keys():
            continue
        out = int(word[-1])
        inb = int(word[-2])
        res_interface[word[0]] = {"out": out, "in": inb}
    return res_interface


def save(res_interface):
    if len(res_interface) == 0:
        return
    ft = open(traffic_file, "w")
    for key in res_interface.keys():
        ft.write(key + " " + str(res_interface[key]["out"]) + " " + str(res_interface[key]["in"]) + "\n")
    ft.close()


def load():
    res = {}
    if not os.path.exists(traffic_file):
        return res
    ft = open(traffic_file, "r")
    lines = ft.readlines()
    ft.close()
    for line in lines:
        item = line.split()
        res[item[0]] = {"out": int(item[1]), "in": int(item[2])}
    return res


def load_result():
    res = {}
    if not os.path.exists(traffic_file_day):
        return res
    ft = open(traffic_file_day, "r")
    lines = ft.readlines()
    ft.close()
    for line in lines:
        item = line.split()
        res[item[0]] = {"out": int(item[1]), "in": int(item[2])}
    return res


def byte_human(bytes_size):
    """
    transform byte size into human readable format
    :param bytes_size: the size in byte
    :return: return a string with units
    """
    unit = ""
    val = bytes_size
    if val > 1024:
        val /= 1024.0
        unit = "kB"
    if val > 1024:
        val /= 1024.0
        unit = "MB"
    if val > 1024:
        val /= 1024.0
        unit = "GB"
    if val > 1024:
        val /= 1024.0
        unit = "TB"
    if val > 1024:
        val /= 1024.0
        unit = "PB"
    return "{:3.1f}".format(val) + unit

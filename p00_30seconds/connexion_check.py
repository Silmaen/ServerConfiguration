#!/usr/bin/env python

from common.maintenance import *

datastate = data_dir + "/wanstates.txt"

wan = {
    "bbox": {"ip": "192.168.2.5",
             "routes": ["4.2.2.2", "208.67.222.222", "8.8.4.4", "37.235.1.177"],
             "state": False
             },
    "cle4g": {"ip": "192.168.2.1",
              "routes": ["4.2.2.1", "208.67.220.220", "8.8.8.8", "37.235.1.174"],
              "state": False
              },
}

pingcmd = "ping -q -c 1 -w 1 "

valid_action = ["add", "delete"]


def get_default_routes():
    """
    get the list of the actual default routes
    :return: the list of default routes
    """
    lines = direct_system_exec("route show -inet | grep default")
    default_routes = []
    for line in lines:
        default_routes.append(line.split()[1])
    return default_routes


def route(action, qui):
    if action not in valid_action:
        return
    if qui not in wan.keys():
        return
    cmd = "/sbin/route " + action + " -mpath default " + wan[qui]["ip"]
    silent_system_exec(cmd)


def wan_up(qui):
    if qui not in wan.keys():
        return False
    cmd = pingcmd + wan[qui]["ip"]
    code = silent_system_exec(cmd)
    if code == 0:
        return True
    return False


def wan_online(qui):
    if qui not in wan.keys():
        return False
    for pin in wan[qui]["routes"]:
        cmd = pingcmd + pin
        code = silent_system_exec(cmd)
        if code == 0:
            return True
    return False


def b2o(b):
    if b:
        return "UP"
    else:
        return "DOWN"


def o2b(s):
    return s == "UP"


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    '''
    if os.path.exists(datastate):
        f = open(datastate, "r")
        lines = f.readlines()
        for line in lines:
            it = line.split()
            if it[0] not in wan.keys():
                continue
            wan[it[0]]["state"] = o2b(it[1])
        f.close()
    '''

    for w in wan:
        w["state"] = False
    for it in get_default_routes():
        if it not in wan.keys():
            continue
        wan[it]["state"] = True

    for w in wan.keys():
        state = False
        if wan_up(w):
            if wan_online(w):
                state = True
        if state != wan[w]["state"]:
            logger.log("conn_chk", "wan " + w + " changed state from " + b2o(wan[w]["state"]) + " to " + b2o(state))
            wan[w]["state"] = state
            if not dry_run:
                if state:
                    route("add", w)
                else:
                    route("delete", w)
    '''
    if not dry_run:
        f = open(datastate, "w")
        for w in wan.keys():
            f.write(w + " " + b2o(wan[w]["state"]) + "\n")
        f.close()
    '''


if __name__ == "__main__":
    main()

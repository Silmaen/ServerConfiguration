#!/usr/bin/env python

from common.maintenance import *
import shutil

default_lease_location = "/var/db"
default_lease_file = "dhcpd.leases"
template_zones_location = "/var/nsd/zones/templates/"
zones_location = "/var/nsd/zones/"
lease_list = ["argawaen.net.zone", "192.168.23.reverse.zone"]
backup_dir = data_dir


def read_leases(filename=""):
    if filename == "":
        filename = os.path.join(default_lease_location, default_lease_file)
    if not os.path.exists(filename):
        write_log("lslease", "ERROR: no lease files foud at '" + filename + "'")
        return {}
    ff = open(filename, "r")
    lines = ff.readlines()
    ff.close()
    raw_lease = ""
    leases_raw = []
    for line in lines:
        if "lease " in line:
            raw_lease = line
        line = line.strip()
        raw_lease += line
        if line == "}":
            leases_raw.append(raw_lease)
    result = {}
    for lease in leases_raw:
        address = lease.split()[1].strip()
        items_raw = lease.split("{")[-1].split("}")[0].split(";")
        items = {}
        if "binding state active" not in items_raw:
            continue
        for item in items_raw:
            if "hardware ethernet" in item:
                items["hardware ethernet"] = item.rsplit(' ', 1)[-1]
            if "client-hostname" in item:
                items["client-hostname"] = item.rsplit(' ', 1)[-1].replace('"', '')
        result[address] = items;
    return result


def print_leases(leases):
    print(str(leases))


def generate_zones(leases):
    has_all_template = True
    for lease in lease_list:
        if not os.path.exists(os.path.join(template_zones_location, lease + ".template")):
            write_log("lslease", "ERROR: unable to find the template '" + os.path.join(template_zones_location, lease + ".template") + "'")
            has_all_template = False
    if not has_all_template:
        return
    if len(leases) == 0:
        for lease in lease_list:
            shutil.copy(os.path.join(template_zones_location, lease + ".template"), os.path.join(zones_location, lease))
        return
    f = open(os.path.join(template_zones_location, "argawaen.net.zone.template"), "r")
    dlines = f.readlines()
    f.close()
    f = open(os.path.join(zones_location, "argawaen.net.zone"), "w")
    for line in dlines:
        f.write(line)
        if line.startswith(";;;%%%DYN ADDRESS%%%"):
            for lease_adr in leases.keys():
                name = leases[lease_adr]['client-hostname']
                mline = name + "      IN A            " + lease_adr + "\n"
                f.write(mline)
    f.close()
    f = open(os.path.join(template_zones_location, "192.168.23.reverse.template"), "r")
    rlines = f.readlines()
    f.close()
    f = open(os.path.join(zones_location, "192.168.23.reverse"), "w")
    for line in rlines:
        f.write(line)
        if line.startswith(";;;%%%DYN ADDRESS%%%"):
            for lease_adr in leases.keys():
                name = leases[lease_adr]['client-hostname']
                adrit = lease_adr.split(".")
                revadr = adrit[3] + "." + adrit[2] + "." + adrit[1] + "." + adrit[0]
                mline = revadr + ".in-addr.arpa.    IN      PTR     " + name + ".argawaen.net.\n"
                f.write(mline)
    f.close()


def backup_hosts(leases):
    old_hosts = {}
    new_hosts = {}
    if len(leases) == 0:
        return False
    res = False
    for lease_adr in leases.keys():
        name = leases[lease_adr]['client-hostname']
        new_hosts[name] = lease_adr
    back_hosts = os.path.join(backup_dir, "backhosts")
    if os.path.exists(back_hosts):
        f = open(back_hosts, "r")
        lines = f.readlines()
        f.close()
        for line in lines:
            it = line.split()
            old_hosts[it[0]] = it[1]
    else:
        res = True
    f = open(back_hosts, "w")
    for host in new_hosts.keys():
        f.write(host + " " + new_hosts[host] + "\n")
    f.close()
    if res:
        return res
    if not os.path.exists(os.path.join(zones_location, "argawaen.net.zone")):
        return True
    if not os.path.exists(os.path.join(zones_location, "192.168.23.reverse")):
        return True
    for host in new_hosts.keys():
        if host not in old_hosts.keys():
            return True
        if new_hosts[host] != old_hosts[host]:
            return True
    return False


def main(dry_run: bool = False):
    leases = read_leases()
    if backup_hosts(leases):
        write_log("lslease", "Zone update required")
        if not dry_run:
            generate_zones(leases)
            system_exec("rcctl restart nsd unbound", "lslease")
    else:
        write_log("lslease", "No zone update required")


if __name__ == "__main__":
    main()

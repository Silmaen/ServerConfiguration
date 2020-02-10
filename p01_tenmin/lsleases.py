#!/usr/bin/env python

import os
crscdir=os.getenv("crscdir","/var/maintenance")
import sys
sys.path.insert(0,crscdir)
from common.maintenance import *

default_lease_location="/var/db/"
#default_lease_location=""
default_lease_file="dhcpd.leases"

template_zones_location="/var/nsd/zones/templates/"
#template_zones_location=""

zones_location="/var/nsd/zones/"
#zones_location=""

backup_dir=crscdir+"/data/"

def read_leases(filename=""):
    if filename=="":
        #filename="/var/db/dhcpd.leases"
        filename=default_lease_location+default_lease_file
    if not os.path.exists(filename):
        return {}
    resu=[]
    ff=open(filename,"r")
    lines=ff.readlines()
    ff.close()
    raw_lease=""
    leases_raw=[]
    for line in lines:
        if "lease " in line:
            raw_lease=line
        line=line.strip()
        raw_lease+=line
        if line=="}":
            leases_raw.append(raw_lease)
    resu={}
    for lease in leases_raw:
        address=lease.split()[1].strip()
        items_raw=lease.split("{")[-1].split("}")[0].split(";")
        items={}
        if "binding state active" not in items_raw:
            continue
        for item in items_raw:
            if "hardware ethernet" in item:
                items["hardware ethernet"]=item.rsplit(' ',1)[-1]
            if "client-hostname" in item:
                items["client-hostname"]=item.rsplit(' ',1)[-1].replace('"','')
        resu[address]=items;
    return resu

def print_leases(leases):
    print(str(leases))

def generate_zones(leases):
    if len(leases)==0:
        shutil.copy(template_zones_location+"argawaen.net.zone.template",zones_location+"argawaen.net.zone")
        shutil.copy(template_zones_location+"192.168.23.reverse.template",zones_location+"192.168.23.reverse.zone")
        return
    f=open(template_zones_location+"argawaen.net.zone.template","r")
    dlines=f.readlines()
    f.close()
    f=open(zones_location+"argawaen.net.zone","w")
    for line in dlines:
        f.write(line)
        if line.startswith(";;;%%%DYN ADDRESS%%%"):
            for lease_adr in leases.keys():
                name=leases[lease_adr]['client-hostname']
                mline=name+"      IN A            "+lease_adr+"\n"
                f.write(mline)
    f.close()
    f=open(template_zones_location+"192.168.23.reverse.template","r")
    rlines=f.readlines()
    f.close()
    f=open(zones_location+"192.168.23.reverse","w")
    for line in rlines:
        f.write(line)
        if line.startswith(";;;%%%DYN ADDRESS%%%"):
            for lease_adr in leases.keys():
                name=leases[lease_adr]['client-hostname']
                adrit=lease_adr.split(".")
                revadr=adrit[3]+"."+adrit[2]+"."+adrit[1]+"."+adrit[0]
                mline=revadr+".in-addr.arpa.    IN      PTR     "+name+".argawaen.net.\n"
                f.write(mline)
    f.close()

def backup_hosts(leases):
    old_hosts={}
    new_hosts={}
    res=False
    for lease_adr in leases.keys():
        name=leases[lease_adr]['client-hostname']
        new_hosts[name]=lease_adr
    if os.path.exists(backup_dir+"backhosts"):
        f=open(backup_dir+"backhosts","r")
        lines=f.readlines()
        f.close()
        for line in lines:
            it=line.split()
            old_hosts[it[0]]=it[1]
    else:
        res=True
    f=open(backup_dir+"backhosts","w")
    for host in new_hosts.keys():
        f.write(host+" "+new_hosts[host]+"\n")
    f.close()
    if res:
        return res
    if not os.path.exists(zones_location+"argawaen.net.zone"):
        return True
    if not os.path.exists(zones_location+"192.168.23.reverse"):
        return True
    for host in new_hosts.keys():
        if host not in old_hosts.keys():
            return True
        if new_hosts[host]!=old_hosts[host]:
            return True
    return False

def main():
    leases=read_leases()
    if backup_hosts(leases):
        write_log("lslease","Zone update required")
        generate_zones(leases)
        system_exec("rcctl restart nsd unbound","lslease")
    else:
        write_log("lslease","No zone update required")
        
if __name__ == "__main__":
    main()

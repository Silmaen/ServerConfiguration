#!/usr/bin/env python

import os
crscdir=os.getenv("crscdir","/var/maintenance")
import sys
sys.path.insert(0,crscdir)
from common.maintenance import *

HOST="srv.argawaen.net"
LOGIN="argawaen.net-srvcom"
PASSWORD="Melissa2"
#
IPFILE=datadir+"/old.ip"

def is_online():
    listip=["4.2.2.2","208.67.222.222"]
    basecmd="ping -q -c 1 -w 5 "
    for ip in listip:
        if ping_host(ip):
            return True
    write_log("dynhost","auncun hote connecte")
    return False

def get_externalips():
    if ping_host("myexternalip.com"):
        ip=getHttpPage("http://myexternalip.com/raw")[0]
        if ip=="":
            return "0.0.0.0","0.0.0.0"
        if "." not in ip:
            return "0.0.0.0","0.0.0.0"
        oldip=get_lastip()
        return ip,oldip
    else:
        write_log("dynhost","myexternalip.com is offline")
        return "0.0.0.0","0.0.0.0"

Dyndnshost = "www.ovh.com"
Dyndnsnic = "/nic/update"

def sendtoovh(localip):
    if "." not in HOST:
        write_log("dynhost","Bad hostname: " + HOST)
        return
    #
    # build the query strings
    #
    updateprefix = Dyndnsnic + "?system=dyndns&hostname="
    updatesuffix = "&myip=" + localip + "&wildcard=ON"
    #
    # URL
    #
    url="https://"+Dyndnshost+updateprefix+HOST+updatesuffix
    if not ping_host(Dyndnshost):
       write_log("dynhost","ERROR: "+Dyndnshost+" is offline")
       return
    httpdata=getHttpPage(url,LOGIN,PASSWORD)
    if len(httpdata)==0:
        write_log("dynhost","ERROR: No results")
        return
    #
    # badsys must begin the resulting text and hresponse.status is 200
    if httpdata[0].startswith("badsys"):
        write_log("dynhost","Bad system parameter specified (not dyndns or statdns).")
    # badagent must begin the resulting text and hresponse.status is 200
    elif httpdata[0].startswith("badagent"):
        write_log("dynhost","Badagent contact author at kal@users.sourceforge.net.")
    else:
        # build the results list
        results = []
        lines=httpdata[0].strip()
        # check if we have one result per updatehosts 
        success = 0
        #
        # use logexit to generate output (email if ran from a cronjob)
        #
        if lines.startswith("good"):
            write_log("dynhost",HOST + " " + lines + " -update successful")
            # set the success update flag
            success = 1
        elif lines.startswith("nochg"):
            write_log("dynhost",HOST + " " + lines + " -consider abusive")
        elif lines.startswith("abuse"):
            write_log("dynhost",HOST + " " + lines + " -hostname blocked for abuse")
        elif lines.startswith("notfqdn"):
            write_log("dynhost",HOST + " " + lines + " -FQDN hostnames needed")
        elif lines.startswith("nohost"):
            write_log("dynhost",HOST + " " + lines + " -hostname not found")
        elif lines.startswith("!yours"):
            write_log("dynhost",HOST + " " + lines + " -hostname not yours")
        elif lines.startswith("numhost"):
            write_log("dynhost",HOST + " " + lines + " -send ipcheck.html to support@dyndns.org")
        elif lines.startswith("dnserr"):
            write_log("dynhost",HOST + " " + lines + " -send ipcheck.html to support@dyndns.org")
        else:
            write_log("dynhost",HOST + " " + lines + " -unknown result line")

def main():
    # test si la connexion internet existe
    write_log("dynhost","starting dynhost update")
    if is_online():
        write_log("dynhost","Internet connexion is UP")
        # test de l'ip externe par test sur site externe
        ip,oldip = get_externalips()
        if ip != "0.0.0.0":
            if ip != oldip:
                write_log("dynhost","IP change detected, updating from "+oldip+" to "+ip)
                sendtoovh(ip)
                set_lastip(ip)
            else:
                write_log("dynhost","No IP changes, no update needed")
        else:
            write_log("dynhost","ERROR: unable to retrieve public IP")
            add_mail("DYNHOST\n====")
            add_mail("ERROR while finding public IP")
    else:
        write_log("dynhost","Internet connexion is DOWN")
        set_lastip("0.0.0.0")

if __name__ == "__main__":
    main()
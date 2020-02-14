#!/usr/bin/env python
from common.maintenance import *

HOST = "srv.argawaen.net"
LOGIN = "argawaen.net-srvcom"
PASSWORD = "Melissa2"
#
IPFILE = os.path.join(data_dir, "old.ip")


def is_online():
    list_ip = ["4.2.2.2", "208.67.222.222"]
    for ip in list_ip:
        if ping_host(ip):
            return True
    write_log("is_online", "no connected host")
    return False


def get_externalips():
    if ping_host("myexternalip.com"):
        ip = get_http_page("http://myexternalip.com/raw")[0]
        if ip == "":
            return "0.0.0.0", "0.0.0.0"
        if "." not in ip:
            return "0.0.0.0", "0.0.0.0"
        oldip = get_last_ip()
        return ip, oldip
    else:
        write_log("dynhost", "myexternalip.com is offline")
        return "0.0.0.0", "0.0.0.0"


Dyndnshost = "www.ovh.com"
Dyndnsnic = "/nic/update"


def sendtoovh(localip):
    if "." not in HOST:
        write_log("dynhost", "Bad hostname: " + HOST)
        return
    #
    # build the query strings
    #
    updateprefix = Dyndnsnic + "?system=dyndns&hostname="
    updatesuffix = "&myip=" + localip + "&wildcard=ON"
    #
    # URL
    #
    url = "https://" + Dyndnshost + updateprefix + HOST + updatesuffix
    if not ping_host(Dyndnshost):
        write_log("dynhost", "ERROR: " + Dyndnshost + " is offline")
        return
    httpdata = get_http_page(url, LOGIN, PASSWORD)
    if len(httpdata) == 0:
        write_log("dynhost", "ERROR: No results")
        return
    #
    # badsys must begin the resulting text and hresponse.status is 200
    if httpdata[0].startswith("badsys"):
        write_log("dynhost", "Bad system parameter specified (not dyndns or statdns).")
    # badagent must begin the resulting text and hresponse.status is 200
    elif httpdata[0].startswith("badagent"):
        write_log("dynhost", "Badagent contact author at kal@users.sourceforge.net.")
    else:
        # build the results list
        results = []
        lines = httpdata[0].strip()
        # check if we have one result per updatehosts 
        success = 0
        #
        # use logexit to generate output (email if ran from a cronjob)
        #
        if lines.startswith("good"):
            write_log("dynhost", HOST + " " + lines + " -update successful")
            # set the success update flag
            success = 1
        elif lines.startswith("nochg"):
            write_log("dynhost", HOST + " " + lines + " -consider abusive")
        elif lines.startswith("abuse"):
            write_log("dynhost", HOST + " " + lines + " -hostname blocked for abuse")
        elif lines.startswith("notfqdn"):
            write_log("dynhost", HOST + " " + lines + " -FQDN hostnames needed")
        elif lines.startswith("nohost"):
            write_log("dynhost", HOST + " " + lines + " -hostname not found")
        elif lines.startswith("!yours"):
            write_log("dynhost", HOST + " " + lines + " -hostname not yours")
        elif lines.startswith("numhost"):
            write_log("dynhost", HOST + " " + lines + " -send ipcheck.html to support@dyndns.org")
        elif lines.startswith("dnserr"):
            write_log("dynhost", HOST + " " + lines + " -send ipcheck.html to support@dyndns.org")
        else:
            write_log("dynhost", HOST + " " + lines + " -unknown result line")


def main(dry_run: bool = False):
    # test si la connexion internet existe
    write_log("dynhost", "starting dynhost update")
    if is_online():
        write_log("dynhost", "Internet connexion is UP")
        ip, old_ip = get_externalips()
        if ip != "0.0.0.0":
            if ip != old_ip:
                write_log("dynhost", "IP change detected, updating from " + old_ip + " to " + ip)
                if not dry_run:
                    sendtoovh(ip)
                    set_last_ip(ip)
            else:
                write_log("dynhost", "No IP changes, no update needed")
        else:
            write_log("dynhost", "ERROR: unable to retrieve public IP")
            add_mail("DYNHOST\n====")
            add_mail("ERROR while finding public IP")
    else:
        write_log("dynhost", "Internet connexion is DOWN")
        if not dry_run:
            set_last_ip("0.0.0.0")


if __name__ == "__main__":
    main()

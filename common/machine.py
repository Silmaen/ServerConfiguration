"""
definition of the class machine
"""
import datetime

timeFormat = "%Y-%m-%d %H:%M:%S"


def mac_compare(mac1: str, mac2: str):
    """
    compare 2 mac address (including mac changes through extender)
    :param mac1: first mac to compare
    :param mac2: second mac to comapre
    :return: True if the mac are equal (or equal trough extender mac translation)
    """
    if mac1 == mac2:
        return True
    dmac1 = "02:0f:b5:" + mac1[9:]
    dmac2 = "02:0f:b5:" + mac2[9:]
    if dmac1 == dmac2:
        return True
    return False


def find_in_lease(ip: str, mac: str):
    """
    try to find the machine name in dhcp lease file
    :return: the machine name if found in lease, "Not Found" else
    """
    import os
    leasefile = "/var/db/dhcpd.leases"
    if not os.path.exists(leasefile):
        return "Not Found"
    lf = open(leasefile)
    lines = lf.readlines()
    lf.close()
    currentlease = ""
    currentmac = ""
    currentname = ""
    for line in lines:
        l = line.strip()
        if len(l) == 0:  # avoid blank line
            continue
        if l.startswith("#"):  # avoid comment line
            continue
        if l in ["}"]:
            if currentlease == ip and currentmac == mac and currentname != "":
                return currentname
            currentlease = ""
            currentmac = ""
            currentname = ""
        if l.startswith("lease"):
            currentlease = l.split("lease")[-1].split("{")[0].strip()
            continue
        if l.startswith("hardware ethernet"):
            currentmac = l.split("hardware ethernet")[-1].split(";")[0].strip()
        if l.startswith("client-hostname"):
            currentname = l.split('"', 1)[-1].split('"')[0].strip().lower()
    return "Not Found"


class Machine:
    """
    object to handle the machine data coming from database
    """

    def __init__(self, name: str = "", mac: str = "", ip: str = "", outmachine: bool = False,
                 started: datetime = datetime.datetime.now()):
        self.name = name
        self.mac = mac
        self.ip = ip
        self.outmachine = outmachine
        self.started = started
        self.inDB = False
        self.inDNS = False
        self.inDNStemplate = False
        self.inLease = False

    def __str__(self):
        ret = [" ", "D"][self.inDB] + [" ", "N"][self.inDNS] + [" ", "L"][self.inLease] + " " + \
              self.mac + " " + self.get_time_str() + " " + self.ip
        for i in range(15 - len(self.ip)):
            ret += " "
        ret += " " + self.name
        return ret

    def set_time(self, time: str):
        """
        set the timestamp of the first machine connexion based on a standard string
        :param time: the string to parse for time
        """
        self.started = datetime.datetime.strptime(time, timeFormat)

    def get_time_str(self):
        """
        get a standard string for the starting time
        :return:
        """
        return self.started.strftime(timeFormat)

    def retrieve_name_from_ip(self):
        """
        get base information about the host
        """
        import socket
        try:
            self.name, a, b = socket.gethostbyaddr(self.ip)
            self.inDNS = True
        except:
            self.name = find_in_lease(self.ip, self.mac)
            if self.name != "Not Found":
                self.inLease = True

    def get_short_name(self):
        """
        get a short name for the machine
        :return: name of the machine without domain
        """
        return self.name.split(".", 1)[0]

    def need_dns_update(self):
        return self.inLease and not self.inDNS

    def need_db_update(self):
        return not self.inDB and "srv.argawaen.net" not in self.name

    def make_dns_entry(self):
        return self.get_short_name() + "\tIN\tA\t" + self.ip

    def make_dns_reverse_entry(self):
        ipids = self.ip.split(".")
        return ipids[3] + "." + ipids[2] + "." + ipids[1] + "." + ipids[
            0] + ".in-addr.arpa.\tIN\tPTR\t" + self.get_short_name()

"""
definition of the class machine
"""
import datetime
from common.databasehelper import DatabaseHelper
from common.maintenance import logger

timeFormat = "%Y-%m-%d %H:%M:%S"


def mac_compare(mac1: str, mac2: str):
    """
    compare 2 mac address (including mac changes through extender)
    :param mac1: first mac to compare
    :param mac2: second mac to compare
    :return: True if the mac are equal (or equal trough extender mac translation)
    """
    m1 = mac1.lower()
    m2 = mac2.lower()
    if m1 == m2:
        return True
    dm1 = "02:0f:b5:" + m1[9:]
    dm2 = "02:0f:b5:" + m2[9:]
    if dm1 == m2 or dm2 == m1:
        return True
    return False


def str_is_ip(string: str):
    """
    determine if the given string represent an IP
    :param string: the string to test
    :return: True if the string has a valid IP format
    """
    items = string.split(".")
    if len(items) != 4:
        return False
    try:
        for i in range(4):
            items[i] = int(items[i])
    except:
        return False
    for i in items:
        if i < 0 or i > 255:
            return False
    return True


def find_in_lease(ip: str, mac: str):
    """
    try to find the machine name in dhcp lease file
    :return: the machine name if found in lease, "Not Found" else
    """
    import os
    lease_file = "/var/db/dhcpd.leases"
    if not os.path.exists(lease_file):
        return "Not Found"
    lf = open(lease_file)
    lines = lf.readlines()
    lf.close()
    current_lease = ""
    current_mac = ""
    current_name = ""
    for line in lines:
        clear_line = line.strip()
        if len(clear_line) == 0:  # avoid blank line
            continue
        if clear_line.startswith("#"):  # avoid comment line
            continue
        if clear_line in ["}"]:
            if current_lease == ip and current_mac == mac and current_name != "":
                return current_name
            current_lease = ""
            current_mac = ""
            current_name = ""
        if clear_line.startswith("lease"):
            current_lease = clear_line.split("lease")[-1].split("{")[0].strip()
            continue
        if clear_line.startswith("hardware ethernet"):
            current_mac = clear_line.split("hardware ethernet")[-1].split(";")[0].strip()
        if clear_line.startswith("client-hostname"):
            current_name = clear_line.split('"', 1)[-1].split('"')[0].strip().lower()
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
        """
        Determine if this machine need dns update
        :return: true if dns update is required
        """
        return self.inLease and not self.inDNS

    def need_db_update(self):
        """
        Determine if this machine need to be updated in db
        :return: true if the machine is not actualized with db
        """
        return not self.inDB and "srv.argawaen.net" not in self.name

    def make_dns_entry(self):
        """
        Construct a dns entry for this machine
        :return: a dns entry
        """
        return self.get_short_name() + "\tIN\tA\t" + self.ip

    def make_dns_reverse_entry(self):
        """
        Construct a reverse dns entry for this machine
        :return: a rdns entry
        """
        ipids = self.ip.split(".")
        return ipids[3] + "." + ipids[2] + "." + ipids[1] + "." + ipids[
            0] + ".in-addr.arpa.\tIN\tPTR\t" + self.get_short_name()


def get_active_machine_db():
    """
    get active machines in DB
    :return: list of machine in DB
    """
    db = DatabaseHelper()
    ret, machines = db.select("ActiveMachine")
    if not ret:
        logger.log("ActiveMachineDb", "Connexion problems")
        return []
    ret = []
    for m in machines:
        mm = Machine(m["MachineName"], m["MAC Address"], m["IP"], m["OutMachine"], m["ConnexionStart"])
        mm.inDB = True
        ret.append(mm)
    return ret

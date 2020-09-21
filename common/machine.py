"""
definition of the class machine
"""
import datetime
from common.databasehelper import DatabaseHelper
from common.maintenance import logger, system_exec

timeFormat = "%Y-%m-%d %H:%M:%S"
extender_mac_prefix = "02:0f:b5:"


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
    dm1 = extender_mac_prefix + m1[9:]
    dm2 = extender_mac_prefix + m2[9:]
    if dm1 == m2 or dm2 == m1:
        return True
    return False


def get_true_mac(mac1: str, mac2: str):
    """
    get the real mac between the 2 given (base on extender mac change)
    :param mac1:
    :param mac2:
    :return:
    """
    if not mac_compare(mac1, mac2):
        return "00:00:00:00:00:00"
    if mac1.startswith(extender_mac_prefix):
        return mac2
    return mac2


def str_is_ip(string: str):
    """
    determine if the given string represent an IP
    :param string: the string to test
    :return: True if the string has a valid IP format
    """
    import socket
    try:
        socket.inet_aton(string)
    except OSError:
        return False
    return True


def str_is_mac(string: str):
    """
    determine if a string is a mac adress
    :param string: the string to test
    :return: True if the string correspond to a MAC address
    """
    import re
    return re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", string.lower())


def is_valid_mac(mac: str):
    """
    return True if the mac address is a valid one
    :param mac:
    :return:
    """
    return mac != "00:00:00:00:00:00" and str_is_mac(mac)


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
        self.disconnected = started
        self.active = True
        self.inDB = False
        self.inDNS = False
        self.inDNStemplate = False
        self.inLease = False
        self.better_mac = False

    def __str__(self):
        ret = [" ", "D"][self.inDB] + [" ", "N"][self.inDNS] + [" ", "L"][self.inLease] + " " + \
              self.mac + " " + self.get_time_str() + " " + self.ip
        for i in range(15 - len(self.ip)):
            ret += " "
        ret += " " + self.name
        return ret

    def __lt__(self, other):
        import socket
        return socket.inet_aton(self.ip) < socket.inet_aton(other.ip)

    def __eq__(self, other):
        return mac_compare(self.mac, other.mac) and self.ip == other.ip and self.name == other.name

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
        except Exception as err:
            self.name = find_in_lease(self.ip, self.mac)
            if self.name != "Not Found":
                self.inLease = True
            else:
                logger.log_error("Machine", "Problem while getting name of machine at ip: " + self.ip +
                                 " err:" + str(err))

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
        logger.log_error("ActiveMachineDb", "Connexion problems")
        return []
    ret = []
    for m in machines:
        mm = Machine(m["MachineName"], m["MAC Address"], m["IP"], m["OutMachine"], m["ConnexionStart"])
        mm.inDB = True
        mm.active = False
        ret.append(mm)
    return ret


def get_connected_since(start):
    """
    get active machines in DB
    :param start:
    :return: list of machine in DB
    """
    db = DatabaseHelper()
    ret, machines = db.select("ConnexionArchive", " WHERE `ConnexionEnd` > '" + str(start) +
                              "' ORDER BY `MachineName` ASC")
    if not ret:
        logger.log_error("ConnexionArchiveDb", "Connexion problems")
        return []
    ret = []
    for m in machines:
        mm = Machine(m["MachineName"], m["MAC Address"], m["IP"], m["OutMachine"], m["ConnexionStart"])
        mm.active = False
        mm.disconnected = m["ConnexionEnd"]
        ret.append(mm)
    return ret


def get_connected_machines():
    """
    get the actual list of connected machines
    :return: list of machine connected
    """
    ret, lines = system_exec("arp -a")
    if ret != 0:
        logger.log_error("Machine", "unable to find connected machine")
        return []
    ret, lines2 = system_exec("arp -an")
    if ret != 0:
        logger.log_error("Machine", "unable to find connected machine")
        return []
    ret = []
    ips = {}
    for line in lines2:
        host, mac, _ = line.split(None, 2)
        ips[mac] = host
    for line in lines:
        if line.startswith("Host"):
            continue
        host, mac, conif, timing = line.split(None, 3)
        if "(incomplete)" in mac:
            continue
        if 'expired' in timing:
            continue
        if "srv.argawaen.net" in host:  # ignore self
            continue
        ip = ips[mac]
        """
        try:
            ip = socket.gethostbyname(host)
        except Exception as err:
            logger.log_error("Machine", "unable to machine IP: '" + host + "' :" + str(err))
            ip = "0.0.0.0" 
        """
        mach = Machine(name=host, ip=ip, mac=mac, outmachine=(conif == "re0"))
        mach.active = True
        ret.append(mach)
    return ret


def get_compared_machine_lists():
    """
    merge the list of machines

    :return:
    """
    m_db = get_active_machine_db()
    m_arp = get_connected_machines()
    ret = []
    # treat machines that are in both lists
    for mach in m_db:
        found = False
        # treat machines that are in both lists
        for mach2 in m_arp:
            if mach == mach2:
                mach.active = True
                mac = get_true_mac(mach.mac, mach2.mac)
                if is_valid_mac(mac) and mac != mach.mac:
                    mach.mac = mac
                    mach.better_mac = True
                ret.append(mach)
                found = True
                break
        if found:
            continue
        # treat machine that are in DB but no more active
        mach.active = False
        ret.append(mach)
    # Treat newly active machine
    for mach in m_arp:
        if mach in ret:  # already treated
            continue
        ret.append(mach)
    ret.sort()
    return ret


def update_active_machine_database():
    """
    compare lists of machine and update the database accordingly
    :return:
    """
    machines = get_compared_machine_lists()
    db = DatabaseHelper()
    for machine in machines:
        mac_dict = {
                "MachineName": machine.name,
                "IP": machine.ip,
                "MAC Address": machine.mac,
                "ConnexionStart": machine.started,
                "OutMachine": [0, 1][machine.outmachine]
            }
        if machine.inDB:
            e_id = db.get_id("ActiveMachine", mac_dict)
            if e_id < 0:
                logger.log_error("machine compare", "ERROR: unable to get ID for " + str(machine))
                continue
            if machine.active:
                # machine already in DB ans still active: does the mac to be updated?
                mac_dict["ID"] = e_id
                if machine.better_mac:
                    db.modify("ActiveMachine", mac_dict)
                continue
            else:
                # newly disconnected machine
                db.delete("ActiveMachine", e_id)
                mac_dict["ConnexionEnd"] = datetime.datetime.now()
                db.insert("ConnexionArchive", mac_dict)
        else:
            if machine.active:
                # newly connected machine
                db.insert("ActiveMachine", mac_dict)
            else:
                # machine not in DB and not Active: should notappend
                logger.log_error("machine compare", "SHOULD NOT HAPPEND: machine badly formed: " + str(machine))


def get_machines_since(date):
    """
    check database for the current day content of machine database
    :return:
    """
    cols = ["Name", "IP", "MAC", "external", "Duration", "status"]
    active_machines = get_active_machine_db()
    now = datetime.datetime.now()
    logout_machines = get_connected_since(date)
    ret = []
    for machine in active_machines:
        ret.append([
            machine.name,
            machine.ip,
            machine.mac,
            machine.outmachine,
            now - machine.started,
            "Connected"
        ])
    for machine in logout_machines:
        print(machine)
        if machine not in ret:
            print("machine not in ret")
            ret.append([
                machine.name,
                machine.ip,
                machine.mac,
                machine.outmachine,
                now - machine.started,
                "Disconnected"
            ])
        else:
            print("machine already in ret")
            for i in range(len(ret)):
                if ret[i] != machine:
                    continue
                if not is_valid_mac(ret[i][2]):
                    ret[i][2] = get_true_mac(machine.mac, ret[i][2])
                ret[i][3] += machine.disconnected - machine.started
                break
    return cols, ret


def get_current_day_machines():
    """
    check database for the current day content of machine database
    :return:
    """
    now = datetime.datetime.now()
    day_begin = datetime.datetime(now.year, now.month, now.day)
    return get_machines_since(day_begin)

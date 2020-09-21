
from common.maintenance import logger
from common.MailingSystem import add_paragraph_with_array
from common.machine import get_current_day_machines, get_machines_since
import datetime


def network():
    """
    compute network statistics
    :return:
    """
    date = datetime.datetime(2020, 7, 1)
    titles, rows = get_machines_since(date)
    logger.log("daily", "Connected machines:")
    logger.log("daily", "\n".join(["\t".join(titles)] + ["\t".join([str(i) for i in r]) for r in rows]))
    # add_paragraph_with_array("Connected machines", col_titles=titles, rows=rows)


class Interface:
    """
    class for interface information
    """
    def __init__(self, type_i, mac):
        self.type = type_i
        self.mac = mac


class KnownMachine:
    """
    Class for holding knwon machine info from database
    """
    def __init__(self, name, type_m, aliases, if_str, ips, comments):
        self.name = name
        self.type = type_m
        self.alias = aliases.split("|")
        self.interfaces = []
        self.set_interface_from_string(if_str)
        self.ips = ips.split("|")
        self.comments = comments

    def set_interface_from_string(self, if_str):
        """
        set interface based on the database string
        :param if_str:
        :return:
        """
        self.interfaces = []
        for ifn in if_str.split("|"):
            t, m = ifn.split(":", 1)
            self.interfaces.append(Interface(t, m))


def get_known_machines():
    """
    get the list of knwon machine from the database server
    :return: list of known machines
    """
    from common.databasehelper import DatabaseHelper
    db = DatabaseHelper()
    resu = db.select("KnownMachines")
    m_list = []
    for res in resu:
        m_list.append(KnownMachine(
                res["Name"],
                res["Type"],
                res["Alias"],
                res["Interfaces"],
                res["Ips"],
                res["Comment"]
        ))
    return m_list


def main(dry_run: bool = False):
    """
    do the job
    :param dry_run: not a true execution
    """
    if not dry_run:
        network()

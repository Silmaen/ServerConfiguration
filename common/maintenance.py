"""
common helper functions
"""
import time
from common.AllDefaultParameters import *
from common.LoggingSystem import Logger

mail_file_txt = os.path.join(data_dir, "mail.txt")

logger = Logger()

ip_file = data_dir + "/old.ip"


def initloger(lg_file, verbose):
    global logger
    logger = Logger(lg_file, verbose)


def system_exec(cmd: str, who: str = "", what: str = ""):
    """
    execute a system command
    :param cmd: the command to run
    :param who: who is trying to use the command
    :param what: message that replace the full command in log in case of error
    :return: (return code, output lines as list of string)
    """
    import subprocess
    if cmd == "":
        return -1, []
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    except (ValueError, OSError) as err:
        twho = who
        if twho == "":
            twho = "robot"
        if what == "":
            msg = "ERROR executing " + cmd
        else:
            msg = "ERROR executing " + what
        logger.log_error(twho, msg)
        return -2, []
    try:
        enc = os.device_encoding(1)
        if not enc:
            enc = "ascii"
        lines = p.stdout.decode(enc, errors='ignore').splitlines()
    except:
        return -3, []
    return p.returncode, lines


def direct_system_exec(cmd: str):
    import subprocess
    if cmd == "":
        return 1, []
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        enc = os.device_encoding(1)
        if not enc:
            enc = "ascii"
        lines = p.stdout.decode(enc, errors='ignore').splitlines()
    except:
        return 1, []
    return p.returncode, lines


def silent_system_exec(cmd: str):
    import subprocess
    if cmd == "":
        return 1
    try:
        return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True).returncode
    except:
        return 1


def get_last_ip():
    old_ip = "0.0.0.0"
    if os.path.exists(ip_file):
        ffi = open(ip_file)
        old_ip = ffi.readline().strip()
        ffi.close()
    return old_ip


def set_last_ip(new_ip):
    from common.machine import str_is_ip
    if not str_is_ip(new_ip):
        return
    ffi = open(ip_file, 'w')
    ffi.write(new_ip.strip())
    ffi.close()


def ping_host(host):
    base_cmd = "ping -q -c 1 -w 5 " + host
    ret, lines = system_exec(base_cmd, "ping_host")
    if ret != 0:
        return False
    items = []
    for line in lines:
        if "packets transmitted," not in line: continue
        items = line.split(",")
        break
    if len(items) != 3:
        return False
    try:
        nb_tran = int(items[0].strip().split()[0])
        nb_received = int(items[1].strip().split()[0])
    except:
        logger.log_error("ping_host", "ERROR in results" + str(items))
        return False
    if nb_tran == nb_received:
        return True
    return False


def get_host_ip(host):
    base_cmd = "ping -q -c 1 -w 5 " + host
    ret, lines = system_exec(base_cmd, "ping_host")
    if len(lines) == 0 or ret != 0:
        return "0.0.0.0"
    if "(" not in lines[0] or ")" not in lines[0]:
        return "0.0.0.0"
    return lines[0].split("(", 1)[-1].split(")", 1)[0]


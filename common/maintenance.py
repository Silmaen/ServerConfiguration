"""
common helper functions
"""
import os
import time
import base64
import http.client
import urllib.parse
from common.AllDefaultParameters import *
from common.LoggingSystem import Logger

mail_file_txt = os.path.join(data_dir, "mail.txt")

logger = Logger()

ip_file = data_dir + "/old.ip"


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
        logger.log(twho, msg, 0)
        return -2, []
    try:
        enc = os.device_encoding(1)
        if not enc:
            enc = "ascii"
        lines = p.stdout.decode(enc, errors='ignore').splitlines()
    except:
        return -3, []
    return p.returncode, lines


def is_system_production():
    """
    check if the system is runing in production mode
    :return: True if the system is in installed directory
    """
    if local_path == "/var/maintenance":
        return True
    return False


def get_last_ip():
    old_ip = "0.0.0.0"
    if os.path.exists(ip_file):
        ffi = open(ip_file)
        old_ip = ffi.readline().strip()
        ffi.close()
    return old_ip


def set_last_ip(new_ip):
    items = new_ip.strip().split(".")
    if len(items) != 4:
        logger.log("set_last_ip", "Wrong number of items in IP '" + str(new_ip) + "'")
        return
    try:
        p1 = int(items[0])
        p2 = int(items[1])
        p3 = int(items[2])
        p4 = int(items[3])
    except:
        logger.log("set_last_ip", "Wrong number format in IP '" + str(new_ip) + "'")
        return
    if p1 < 0 or 255 < p1:
        logger.log("set_last_ip", "Wrong number value in IP '" + str(new_ip) + "'")
        return
    if p2 < 0 or 255 < p2:
        logger.log("set_last_ip", "Wrong number value in IP '" + str(new_ip) + "'")
        return
    if p3 < 0 or 255 < p3:
        logger.log("set_last_ip", "Wrong number value in IP '" + str(new_ip) + "'")
        return
    if p4 < 0 or 255 < p4:
        logger.log("set_last_ip", "Wrong number value in IP '" + str(new_ip) + "'")
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
        logger.log("ping_host", "ERROR in results" + str(items))
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


def get_http_response(url: str, user: str = "", password: str = ""):
    valid_type = ["http", "https"]
    if "://" not in url:
        url = "http://" + url
    dec = urllib.parse.urlparse(url)
    if "." not in dec.netloc:
        logger.log("exist_http_page", "Bad hostname: " + dec.netloc)
        return False
    try:
        if dec.scheme == "http":
            h2 = http.client.HTTPConnection(dec.netloc, timeout=50)
        elif dec.scheme == "https":
            h2 = http.client.HTTPSConnection(dec.netloc, timeout=50)
        else:
            logger.log("exist_http_page", "unsupported dec.scheme: '" + dec.scheme + "' valid type: " + str(valid_type))
            return False
    except TimeoutError as err:
        logger.log("exist_http_page", "Error: Request to: " + str(dec.netloc) + " has timed out!!")
        return False
    request = dec.path
    if dec.query != "":
        request += "?" + dec.query
    h2.putrequest("GET", request)
    if user != "":
        auth_str = user + ":" + password
        auth_string = base64.b64encode(auth_str.encode("ascii")).decode("ascii").replace('\n', '')
        h2.putheader("AUTHORIZATION", "Basic " + auth_string)
    h2.endheaders()
    return h2.getresponse()


def exist_http_page(url: str, user: str = "", password: str = ""):
    http_response = get_http_response(url, user, password)
    if http_response.status == 200:
        return True
    else:
        return False


def get_http_page(url: str, user: str = "", password: str = ""):
    http_response = get_http_response(url, user, password)
    try:
        http_data = http_response.read().decode("ascii").splitlines()
    except:
        http_data = []
    if http_response.status == 200:
        return http_data
    logger.log("getHttpPage", "ERROR " + str(http_response.status) + " : " + str(http_response.reason))
    return http_data


def add_mail(message):
    if not os.path.exists(mail_file_txt):
        ffi = open(mail_file_txt, "w")
        ffi.write("Activity report from argawaen.net server\n")
        ffi.write("======\n\n")
        ffi.write(time.strftime("%Y %h %d %H:%M:%S") + "\n")
    else:
        ffi = open(mail_file_txt, "a")
    ffi.write(message + "\n")
    ffi.close()


def flush_mail():
    if os.path.exists(mail_file_txt):
        os.remove(mail_file_txt)

#!/usr/bin/env python
"""
script for ban list actualization
"""
from common.maintenance import *


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    # variables
    server = "https://lists.blocklist.de/lists"
    testlist = "all.txt"
    ban_ip_table = "ban_ip"
    ban_ip_file = "/etc/banlist"
    #
    logger.log("actualize_ban", "Actualization banlist from " + server + "/" + testlist)
    lines = get_http_page(server + "/" + testlist)
    if len(lines) == 0:
        logger.log("actualize_ban", "ERROR: no addess in received list")
        return
    if not dry_run:
        ffi = open(ban_ip_file, "w")
        for line in lines:
            ffi.write(line + "\n")
        ffi.close()
        # -- actualize table in pf --
        cmd = "pfctl -t " + ban_ip_table + " -T replace -f /etc/banlist"
        ret, lines = system_exec(cmd, "actualize_ban", " banlist update")
        for line in lines:
            logger.log("actualize_ban", line)


if __name__ == "__main__":
    main()

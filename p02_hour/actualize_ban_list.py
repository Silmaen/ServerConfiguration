#!/usr/bin/env python
from common.maintenance import *


def main(dry_run: bool = False):
    # variables
    server = "https://lists.blocklist.de/lists"
    testlist = "all.txt"
    ban_ip_table = "ban_ip"
    ban_ip_file = "/etc/banlist"
    #
    write_log("actualize_ban", "Actualization banlist from " + server + "/" + testlist)
    lines = get_http_page(server + "/" + testlist)
    if len(lines) == 0:
        write_log("actualize_ban", "ERROR: no addess in received list")
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
            write_log("actualize_ban", line)


if __name__ == "__main__":
    main()

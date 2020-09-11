#!/usr/bin/env python
# -*- coding : utf-8 -*-
"""
check and log the machines on the network
"""
from common.machine import update_active_machine_database


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    if not dry_run:
        update_active_machine_database()


if __name__ == "__main__":
    main()

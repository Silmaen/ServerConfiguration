#!/usr/bin/env python
"""
procedure to force the new syslog even if not needed
"""
from common.maintenance import *


def newsyslog_forced():
    """
    monthly log rotate has to be forced
    :return:
    """
    logger.log("monthly", "newsyslog forced")
    ret, lines = system_exec("/usr/bin/newsyslog -F")
    if len(lines) != 0:
        # il y a un probleme
        logger.log_error("monthly", "problem in newsyslog execution")
        add_mail("Problems in newsyslog execution\n====")
        add_mail("[VERBATIM]")
        for line in lines:
            logger.log("monthly", line)
            add_mail(line)
        add_mail("[/VERBATIM]")


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    if not dry_run:
        newsyslog_forced()


if __name__ == "__main__":
    main()

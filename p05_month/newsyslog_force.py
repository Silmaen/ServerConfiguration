#!/usr/bin/env python
"""
procedure to force the new syslog even if not needed
"""
from common.maintenance import logger, system_exec
from common.MailingSystem import add_paragraph_with_lines


def newsyslog_forced():
    """
    monthly log rotate has to be forced
    :return:
    """
    logger.log("monthly", "newsyslog forced")
    ret, lines = system_exec("/usr/bin/newsyslog -F")
    if len(lines) != 0:
        # il y a un probleme
        logger.log_error("monthly", "problem in newsyslog execution\n" + "\n".join(lines))
        add_paragraph_with_lines("newsyslog", pre_message=["problem in newsyslog execution"],
                                 lines=lines)


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

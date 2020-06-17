#!/usr/bin/env python
"""
script to generate a mail error report if too many errors occurs
"""
from common.maintenance import add_mail
from common.LoggingSystem import get_error_list
from datetime import datetime


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    if dry_run:
        return
    now = datetime.now()
    past = now.replace(hour=now.hour-1)
    errors = get_error_list(past, now)
    if len(errors) > 10:
        add_mail("Too Many Errors in one Hour:\n")
        for err in errors:
            add_mail(str(err))


if __name__ == "__main__":
    main()

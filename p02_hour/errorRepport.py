#!/usr/bin/env python
"""
script to generate a mail error report if too many errors occurs
"""
from common.LoggingSystem import get_error_list
from datetime import datetime, timedelta
from common.MailingSystem import new_mail, add_paragraph_with_array


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    if dry_run:
        return
    now = datetime.now()
    past = now - timedelta(hours=1)
    errors = get_error_list(past, now)
    if len(errors) > 10:
        errors_md = []
        for err in errors:
            errors_md.append(err.to_md_array())
        add_paragraph_with_array("Too Many Errors in one Hour", col_titles=["time", "who", "message"], rows=errors_md)


if __name__ == "__main__":
    main()

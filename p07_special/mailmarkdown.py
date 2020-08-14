"""
test to transform a markdown to html
"""
from common.MailingSystem import generate_htmlfile


def main(dry_run: bool = False):
    """
    do the job
    :param dry_run: not a true execution
    """
    if not dry_run:
        generate_htmlfile()

"""
procedure for testing
"""
from common.maintenance import *


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    if dry_run:
        write_log("Testing", "Main testing Procedure dry run")
    else:
        write_log("Testing", "Main testing Procedure")


if __name__ == "__main__":
    main()

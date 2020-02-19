from common.maintenance import *


def main(dry_run: bool = False):
    if dry_run:
        write_log("Testing", "Main testing Procedure dry run")
    else:
        write_log("Testing", "Main testing Procedure")


if __name__ == "__main__":
    main()

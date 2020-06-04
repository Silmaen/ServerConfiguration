# /usr/bin/env python
# encoding: utf-8

from common.Connexion_DB import *

MySQLParams = {
    'host': "localhost",
    'user': "robot",
    'passwd': "Robot123",
    'db': "adiministration"
}


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    if dry_run:
        write_log("ClientStatistics", "Check for client stat dry run")
    else:
        write_log("ClientStatistics", "Check for client stat")
    ending = datetime.datetime.now()
    starting = ending - datetime.timedelta(days=1)
    db = MyDataBase(MySQLParams, "ClientStatistic")
    if not db.db_connexion():
        write_log("ClientStatistics", "Unable to get the database")
        return
    machine_list = db.get_connexions_between(starting, ending)
    lines = print_machine_list_duration(machine_list)
    write_log("daily", "Connected machines:")
    add_mail("Connected machines\n===")
    add_mail("[VERBATIM]")
    for line in lines:
        write_log("daily", line)
        add_mail(line)
    add_mail("[/VERBATIM]")


if __name__ == "__main__":
    main()

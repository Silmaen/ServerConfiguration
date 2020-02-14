#!/usr/bin/env python

from common.maintenance import *
import argparse
import common.mailing as mailing

the_date = datetime.datetime.now()
tomorrow_date = the_date + datetime.timedelta(days=1)


def run_30sec(dry_run: bool = False):
    if dry_run:
        write_log("robot", "Dry run procedure for testing 30 seconds procedures")
    from p00_30seconds import connexion_check, connexion_table
    connexion_check.main(dry_run)
    connexion_table.main(dry_run)


def run_10min(dry_run: bool = False):
    if dry_run:
        write_log("robot", "Dry run procedure for testing 10 minutes procedures")
    else:
        write_log("exec", "run 10 minutes procedures")
    from p01_tenmin import dynhost, lsleases, pflogrotate, trafic
    dynhost.main(dry_run)
    lsleases.main(dry_run)
    pflogrotate.main(dry_run)
    trafic.main(dry_run)


def run_hourly(dry_run: bool = False):
    run_10min(dry_run)
    if dry_run:
        write_log("robot", "Dry run procedure for testing hourly procedures")
    else:
        write_log("exec", "run hourly procedures")
    from p02_hour import actualize_ban_list, newsyslog
    actualize_ban_list.main(dry_run)
    newsyslog.main(dry_run)


def run_daily(dry_run: bool = False):
    run_hourly(dry_run)
    if dry_run:
        write_log("robot", "Dry run procedure for testing daily procedures")
    else:
        write_log("exec", "run daily procedures")
    from p03_day import daily, test_newversion, traffic_day
    daily.main(dry_run)
    test_newversion.main(dry_run)
    traffic_day.main(dry_run)


def run_weekly(dry_run: bool = False):
    run_daily(dry_run)
    if dry_run:
        write_log("robot", "Dry run procedure for testing weekly procedures")
    else:
        write_log("exec", "run weekly procedures")
    from p04_week import weekly
    weekly.main(dry_run)


# monthly & yearly are specials


def run_monthly(last: bool = False, dry_run: bool = False):
    if dry_run:
        write_log("robot", "Dry run procedure for testing monthly procedures")
    else:
        write_log("exec", "run monthly procedures")
    from p05_month import newsyslog_force
    newsyslog_force.main(dry_run)
    #
    # pack monthly
    #
    cwd = os.getcwd()
    os.chdir(log_dir)
    if os.path.exists(logfile + "_month_" + str(the_date.year) + "_" + str(the_date.month) + ".tgz"):
        return  # already done
    if os.path.exists(logfile + "_year_" + str(the_date.year) + ".tgz"):
        return  # already done
    cmd = "tar czf " + logfile + "_month_" + str(the_date.year) + "_" + str(the_date.month) + ".tgz " + logfile + ".log"
    if dry_run:
        write_log("monthly", "Packing dry")
        write_log("monthly", ">>> " + cmd)
    else:
        write_log("monthly", "Packing")
        system_exec(cmd)
        if not last:
            new_log()
    os.chdir(cwd)


def run_yearly(dry_run: bool = False):
    run_monthly(True, dry_run)
    if dry_run:
        write_log("robot", "Dry run procedure for testing yearly procedures")
    else:
        write_log("exec", "run yearly procedures")
    # from p06_year import *
    #
    # pack yearly
    #
    cwd = os.getcwd()
    os.chdir(log_dir)
    if os.path.exists(logfile + "_year_" + str(the_date.year) + ".tgz"):
        return  # already done
    cmd = "tar czf " + logfile + "_year_" + str(the_date.year) + ".tgz " + \
          logfile + "_month_" + str(the_date.year) + "_*.tgz "
    if dry_run:
        write_log("yearly", "Packing dry:")
        write_log("yearly", ">>> " + cmd)
        write_log("yearly", ">>> new_log")
    else:
        write_log("yearly", "Packing")
        system_exec(cmd)
        new_log()
    os.chdir(cwd)
    write_log("yearly", "Happy new year!")


def run_special(dry_run: bool = False):
    if dry_run:
        write_log("robot", "Dry run procedure for testing special procedures")
    else:
        write_log("exec", "run special procedures")
    from p07_special import Testing, ClientStatistics
    Testing.main(dry_run)
    ClientStatistics.main(dry_run)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fast", action="store_true",
                        help="Run the script in FAST mode: only 30sec actions no mail")
    parser.add_argument("-s", "--special", action="store_true", help="Run the script in FAST mode: no mail")
    parser.add_argument("-m", "--mailing", action="store_true", help="Run the script in mail-only mode")
    parser.add_argument("-d", "--dry_run", action="store_true",
                        help="Run the script in dry-run mode for testing purpose")
    args = parser.parse_args()

    if args.special:
        run_special()
        return
    if args.fast:
        run_30sec()
        return
    if args.mailing:
        mailing.main(False, True)
        return
    if args.dry_run:
        write_log("robot", "\n\n --- Dry run procedure for testing --- \n")
        run_30sec(True)
        run_weekly(True)
        run_yearly(True)
        mailing.main()
        write_log("robot", "\n\n --- Done Dry run procedure for testing --- \n")
        return

    #
    # run maintenance procedures
    # 
    if the_date.minute >= 50:
        # hourly or only 10min
        if the_date.hour >= 23:
            # daily?
            if the_date.weekday() == 6:
                # weekly?
                run_weekly()
            else:
                run_daily()
        else:
            run_hourly()
    else:
        run_10min()
    #
    # run monthly/yearly procedure
    #
    if tomorrow_date.day == 1:
        # so today is the last month day
        if tomorrow_date.year != the_date.year:
            # so we are at the last day of the year
            run_yearly()
        else:
            run_monthly()
    #
    # mailing procedure
    #
    mailing.main()
    write_log("exec", "--- DONE ---")


if __name__ == "__main__":
    main()

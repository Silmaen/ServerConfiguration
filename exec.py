#!/usr/bin/env python

from common.maintenance import *
import argparse
import common.mailing as mailing

ladate = datetime.datetime.now()
demain = ladate + datetime.timedelta(days=1)

import p00_30seconds.connexion_check as connexion_check
import p00_30seconds.connexion_table as connexion_table
def run_30sec():
    #write_log("exec","run 30sec procedures")
    connexion_check.main()
    connexion_table.main()

import p01_tenmin.dynhost as dynhost
import p01_tenmin.lsleases as lsleases
import p01_tenmin.pflogrotate as pflogrotate
import p01_tenmin.trafic as trafic
def run_10min():
    write_log("exec","run 10 minutes procedures")
    dynhost.main()
    lsleases.main()
    pflogrotate.main()
    trafic.main()

import p02_hour.actualize_ban_list as actualize_ban_list
import p02_hour.newsyslog as newsyslog
def run_hourly():
    run_10min()
    write_log("exec","run hourly procedures")
    actualize_ban_list.main()
    newsyslog.main()

import p03_day.daily as daily
import p03_day.test_newversion as test_newversion
import p03_day.traffic_day as traffic_day
def run_daily():
    run_hourly()
    write_log("exec","run daily procedures")
    daily.main()
    test_newversion.main()
    traffic_day.main()

import p04_week.weekly as weekly
def run_weekly():
    run_daily()
    write_log("exec","run weekly procedures")
    weekly.main()

# monthly & yearly are specials
import p05_month.newsyslog_force as newsyslog_force
def run_monthly():
    write_log("exec","run monthly procedures")
    newsyslog_force.main()
    #
    # pack monthly
    #
    cwd = os.getcwd()
    os.chdir(logdir)
    if os.path.exists(logfile+"_month_"+ladate.year+"_"+ladate.month+".tgz"):
        return # already done
    if os.path.exists(logfile+"_year_"+ladate.year+".tgz"):
        return # already done
    write_log("monthly","Packing")
    lines = system_exec("tar czf "+ logfile +"_month_"+ladate.year+"_"+ladate.month+".tgz "+ logfile +".log")
    new_log()
    os.chdir(cwd)

def run_yearly():
    run_monthly()
    write_log("exec","run yearly procedures")
    #
    # pack yearly
    #
    cwd = os.getcwd()
    os.chdir(logdir)
    if os.path.exists(logfile+"_year_"+ladate.year+".tgz"):
        return # already done
    write_log("yearly","Packing")
    lines = system_exec("tar czf "+logfile+"_year_"+ladate.year+".tgz "+ logfile +"_month_"+ladate.year+"_*.tgz ")
    new_log()
    os.chdir(cwd)
    write_log("yearly","Happy new year!")

import p07_special.ClientStatistics as ClientStatistics
def run_special():
    ClientStatistics.main()

def main():
    Parser = argparse.ArgumentParser()
    Parser.add_argument("-f","--fast",action="store_true",help="Run the script in FAST mode: only 30sec actions no mail")
    Parser.add_argument("-s","--special",action="store_true",help="Run the script in FAST mode: no mail")
    args = Parser.parse_args()
    
    if args.special:
        run_special()
        return
    if args.fast:
        run_30sec()
        return
    #
    # run maintenance procedures
    # 
    if ladate.minute >= 50:
        # hourly or only 10min
        if ladate.hour >= 23:
            #daily?
            if ladate.weekday() == 6:
                #weekly?
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
    if demain.day == 1:
        # alors aujourd'hui est le dernier jour du mois!
        if demain.year != ladate.year:
            # dernier moius de l'année
            run_yearly()
        else:
            run_monthly()
    #
    # mailing procedure
    #
    mailing.main()
    write_log("exec","--- DONE ---")

if __name__ == "__main__":
    main()

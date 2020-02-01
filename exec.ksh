#!/bin/ksh
# script executed every ten minutes
# definition of folder and log
export crscdir=/var/maintenance
export logdir=/var/maintenance/log
export mailfile=/var/maintenance/data/mail.txt
export logfile=maintenance
export fulllogfile=${logdir}/${logfile}.log
# definition of shell launcher
export lpython=/usr/local/bin/python
export lksh=/bin/ksh
export lcsh=/bin/csh
export lsh=/bin/sh
#----------------------------------------------------------------------
minute=$(date +"%M")
hour=$(date +"%H")
day=$(date +"%d")
weekday=$(date +"%w") # 0: sunday 1: monday ..etc..
month=$(date +"%m")
year=$(date +"%Y")
tomorow=$(date -r `expr $(date +%s) + 86400` +\%d)
ymonth=`date +"%Y_%m"`
#----------------------------------------------------------------------
. ${crscdir}/common/maintenance.ksh
# Compress the log file of the month
pack_monthly(){
	cd ${logdir}
	if [[ -f ${logfile}_month_${ymonth}.tgz ]] then
		return
	fi
	if [[ -f ${logfile}_year_${year}.tgz ]] then
		return
	fi
	log_message "log" "Monthly packing"
	tar czf ${logfile}_month_${ymonth}.tgz ${logfile}.log
	new_log
	cd -
}
# Compress the monthly compress log file of the year
pack_yearly(){
	cd ${logdir}
	if [[ ! -f ${logfile}_${ymonth}.tgz ]] then
		pack_monthly
	fi
	tar czf ${logfile}_year_${year}.tgz ${logfile}_month_${year}*.tgz
	rm ${logfile}_month_${year}*.tgz
	log_message "log" "Happy new year!!"
	cd -
}
# execute all script in a directory
execute_dir(){
	basedir=$1
	if [[ -d $basedir ]] then
		list=$(ls $basedir/)
		for f in $list
		do
			extension=$(echo ${f}|awk -F\. '{print $2}')
			if [[ "${extension}" == "py" ]] then
				if [[ -f ${lpython} ]] then
					#log_message "robot" "executing ${f}"
					${lpython} ${1}/${f}
				fi
			fi
			if [[ "${extension}" == "sh" ]] then
				if [[ -f ${lsh} ]] then
					#log_message "robot" "executing ${f}"
					${lsh} ${1}/${f}
				fi
			fi
			if [[ "${extension}" == "ksh" ]] then
				if [[ -f ${lksh} ]] then
					#log_message "robot" "executing ${f}"
					${lksh} ${1}/${f}
				fi
			fi
			if [[ "${extension}" == "csh" ]] then
				if [[ -f ${lcsh} ]] then
					#log_message "robot" "executing ${f}"
					${lcsh} ${1}/${f}
				fi
			fi
		done
	fi
}
#----------------------------------------------------------------------
#====================================
# what is executed every 10mins
#  - all scripts contains in 01_tenmin
log_message "robot" "10min procedure"
basedir=${crscdir}/01_tenmin
execute_dir "$basedir"

if [[ $minute -eq 50 ]] then
	# what is executed every hour at minute '50' not 0
	log_message "robot" "hourly procedure"
	basedir=${crscdir}/02_hour
	execute_dir "$basedir"
	if [[ $hour -eq 23 ]] then
		# what is executed every day: 23:50
		log_message "robot" "daily procedure"
		basedir=${crscdir}/03_day
		execute_dir "$basedir"
		if [[ $weekday -eq 0 ]] then
			# what is executed every week: sunday 23:50
			log_message "robot" "weekly procedure"
			basedir=${crscdir}/04_week
			execute_dir "$basedir"
		fi
		# what is executed every month last day of the month (if tomorow =01 )
		if [[ $tomorow == '01'  ]] then
			log_message "robot" "monthly procedure"
			basedir=${crscdir}/05_month
			execute_dir "$basedir"
			if [[ $month -eq 12 ]] then
				# what is executed every year
				log_message "robot" "yearly procedure"
				basedir=${crscdir}/06_year
				execute_dir "$basedir"
			fi
			pack_monthly
			if [[ $month -eq 12 ]] then
				pack_yearly
			fi
		fi
	fi
fi
#====================================
# finalization: check for mail informations and send it
${lpython} ${crscdir}/common/mailing.py
log_message "robot" "--- DONE ---"

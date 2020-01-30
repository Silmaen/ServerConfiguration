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
# what is executed every 30 sec
#  - all scripts contains in 01_tenmin
#log_message "robot" "30sec procedure"
basedir=${crscdir}/00_30seconds
execute_dir "$basedir"

#====================================
# finalization: check for mail informations and send it
${lpython} ${crscdir}/common/mailing.py
#log_message "robot" "--- DONE ---"

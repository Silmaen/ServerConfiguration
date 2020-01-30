#!/bin/ksh -f

# create a new log file
new_log() {
        echo "`date +"%Y %h %d %H:%M:%S"` [log] : Starting new file" > ${fulllogfile}
}
# write message in log file
log_message(){
        if [[ $1 == "" ]] then
                return
        fi
        echo "`date +"%Y %h %d %H:%M:%S"` [$1] : $2" >> ${fulllogfile}
}

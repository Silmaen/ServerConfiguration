#!/usr/bin/env python

import os
crscdir=os.getenv("crscdir","/var/maintenance")
import sys
sys.path.insert(0,crscdir)
from common.maintenance import *
import subprocess
import common.htmlwrite as htmlwrite
import shutil

# line followed by this line is automatically transformed into 'section title'
#           h1       h2      h3     h4    h5     h6
titlestr =["======","=====","====","===","----","---"]
# syntax coloring: key words
colorstr ={}
colorstr["Ok"]="#00C800"
colorstr["Better"]="#00C800"
colorstr["Passed"]="#00C800"
colorstr["Warning"]="#FFAF00"
colorstr["Worse"]="#FFAF00"
colorstr["Error"]="red"
colorstr["Failed"]="red"
colorstr["Unfeasable"]="red"
# syntax coloring: key lines
colorline ={}
colorline["[V]"]="#8000B8"
#
mainlinglist=["argawaen@argawaen.net"]
#
def convert_mail(strlist):
    hf=htmlwrite.htmlfile(title="[Maintenance] srv.argawaen.net")
    hf.setKeywordColor(colorstr)
    hf.setFormatted(False)
    premode=0
    listniv=0
    for id,line in enumerate(strlist):
        cline=line.strip()
        nline=""
        # retrieving the 'next' line
        if id+1 < len(strlist):
            nline=strlist[id+1]
            nline=nline.strip()
        # VERBATIM mode activation/deactivation
        if cline == "[VERBATIM]":
            hf.addLine("<pre>")
            premode=1
            continue
        if cline == "[/VERBATIM]":
            hf.addLine("</pre>")
            premode=0
            continue
        # if we are in VERBATIM mode: no aditionnal formating
        if premode == 1:
            hf.addLine(cline+"\n")
            continue
        # coloring line
        for key in colorline.keys():
            if cline.startswith(key):
                cline="<font color=\""+colorline[key]+"\">"+cline.lstrip(key).strip()+"</font>"
        #   treatment of an empty line
        if cline == "":
            # if we were in the list, close the list
            if listniv > 0:
                hf.addLine("</ul>")
                listniv=0
            continue
        # if we are in the list, add an item to the list
        if listniv >0 :
            hf.addLine(cline,"li")
            continue
        # if the line ends with ':' then start a list
        if cline.endswith(":"):
            hf.addLine("<ul><b>"+cline+"</b>","")
            listniv+=1
            continue
        # ignore title identifier line
        if cline in titlestr:
            continue
        # check for a title modifier
        if nline in titlestr:
            niv=titlestr.index(nline)+1
            if niv<3:
                hf.addLine("<hr>")
            hf.addSection(cline,niv)
            continue
        # else: this is a standard line, write it into a paragraph
        hf.addParargraph(cline)
    hf.addLine("<hr>")
    return hf.generate()

def restartSmtpd():
    lines = system_exec("rcctl restart smtpd")
    for line in lines:
        if 'failed' in line:
            return False
        if 'ok' not in line:
            return False
    return True

def sendmail(mailfile, mailinglist):
    lines = system_exec("cat " + mailfile + " | sendmail "+mailinglist)
    if len(lines) == 0:
        return True
    # there is a problem
    tempPb = False
    for line in lines:
        if "451" in line:
            tempPb = True
            break
    if not tempPb:
        # this is a true problem
        write_log("mailing","Mail sending problem:")
        for line in lines:
            write_log("mailing",line)
        return False
    # attempt to restart smtpd:
    if not restartSmtpd():
        # error during restart
        write_log("mailing","ERROR: unable to restart smtpd")
        return False
    # resend message
    lines = system_exec("cat " + mailfile + " | sendmail "+mailinglist)
    if len(lines) == 0:
        return True
    write_log("mailing","Mail sending problem:")
    for line in lines:
        write_log("mailing",line)
    return False

def main():
    #
    mailfile=os.getenv("mailfile","/var/maintenance/data/mail.txt")
    if not os.path.exists(mailfile):
        #TODO setup a verbosity level as GLOBAL Variable
        #write_log("mailing","no mail file named:"+mailfile)
        return
    #
    write_log("mailing","Mail need to be sent")
    ffi=open(mailfile,"r")
    lines=ffi.readlines()
    ffi.close()
    htmllines=convert_mail(lines)
    headerlines=[]
    headerlines.append("From: maintenance@argawaen.net")
    stri="To:"
    for mli in mainlinglist:
        stri+=" "+mli
    headerlines.append(stri)
    headerlines.append("Subject: Activity repport from argawaen.net server")
    headerlines.append("Mime-Version: 1.0")
    headerlines.append("Content-Type: text/html")
    mailtxt=open(datadir+"/hmail","w")
    for line in headerlines:
        mailtxt.write(line+"\n")
    mailtxt.write("\n")
    mailtxt.write(htmllines+"\n")
    mailtxt.close()
    stri=" ".join(mainlinglist)
    if not sendmail(os.path.join(datadir,"hmail"),stri):
        # on ne save/flush QUE si le mail est bien parti!
        return
    if not os.path.exists(datadir+"/save"):
        os.makedirs(datadir+"/save")
    shutil.copy2(datadir+"/hmail",datadir+"/save/hmail")
    shutil.copy2(mailfile,datadir+"/save/mail.txt")
    os.remove(datadir+"/hmail")
    flush_mail()

if __name__ == "__main__":
    main()


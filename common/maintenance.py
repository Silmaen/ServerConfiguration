#!/usr/bin/env python

import os
import time
import subprocess
import base64
import http.client
import urllib.parse

localpath="/var/maintenance"
logdir=localpath+"/log"
datadir=localpath+"/data"
logfile="maintenance"
fulllogfile=logdir+"/"+logfile+".log"

def new_log():
    ffi = os.getenv("fulllogfile","")
    if ffi=="":
        ffi=fulllogfile
    f=open(ffi,"w")
    dnow = time.time()
    f.write(time.strftime("%Y %h %d %H:%M:%S")+" [log] : Starting new log file\n")
    f.close()

def write_log(qui,str):
    if qui=="":
        return
    ffi = os.getenv("fulllogfile","")
    if ffi=="":
        ffi=fulllogfile
    f=open(ffi,"a")
    dnow = time.time()
    f.write(time.strftime("%Y %h %d %H:%M:%S")+" ["+qui+"] : "+str+"\n")
    f.close()

ipfile=datadir+"/old.ip"

def get_lastip():
    oldip="0.0.0.0"
    if os.path.exists(ipfile):
        ffi=open(ipfile,'r')
        oldip=ffi.readline().strip()
        ffi.close()
    return oldip;

def set_lastip(newip):
    items=newip.strip().split(".")
    if len(items)!=4:
        write_log("set_lastip","Wrong number of items in IP '"+str(newip)+"'")
        return
    try:
        p1=int(items[0])
        p2=int(items[1])
        p3=int(items[2])
        p4=int(items[3])
    except:
        write_log("set_lastip","Wrong number format in IP '"+str(newip)+"'")
        return
    if p1<0 or 255<p1:
        write_log("set_lastip","Wrong number value in IP '"+str(newip)+"'")
        return
    if p2<0 or 255<p2:
        write_log("set_lastip","Wrong number value in IP '"+str(newip)+"'")
        return
    if p3<0 or 255<p3:
        write_log("set_lastip","Wrong number value in IP '"+str(newip)+"'")
        return
    if p4<0 or 255<p4:
        write_log("set_lastip","Wrong number value in IP '"+str(newip)+"'")
        return
    ffi=open(ipfile,'w')
    ffi.write(newip.strip())
    ffi.close()

def system_exec(cmd,who="",what=""):
    if type(cmd)!=str:
        return []
    if type(who)!=str:
        return []
    if type(what)!=str:
        return []
    if cmd=="":
        return []
    try:
        out, _ = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True).communicate()
    except (ValueError, OSError) as err:
        twho=who
        if twho=="":
            twho="robot"
        if what=="":
            msg="ERROR executing "+cmd
        else:
            msg="ERROR executing "+what
        write_log(twho,msg)
        return
    lines=out.decode("utf-8").splitlines()
    return lines

def ping_host(host):
    basecmd="ping -q -c 1 -w 5 "+host
    lines=system_exec(basecmd,"ping_host")
    morceaux=[]
    for line in lines:
        if "packets transmitted," not in line: continue
        morceaux=line.split(",")
        break
    if len(morceaux)!=3:
        return False
    try:
        nbtran=int(morceaux[0].strip().split()[0])
        nbrece=int(morceaux[1].strip().split()[0])
    except:
        write_log("ping_host","ERREUR de resultat"+str(morceaux))
        return False
    if nbtran==nbrece:
        return True
    return False

def get_host_ip(host):
    basecmd="ping -q -c 1 -w 5 "+host
    lines=system_exec(basecmd,"ping_host")
    if len(lines)==0:
        return "0.0.0.0"
    if not "(" in lines[0] or ")" not in lines[0]:
        return "0.0.0.0"
    return lines[0].split("(",1)[-1].split(")",1)[0]

def existHttpPage(url,user="",password=""):
    if type(url)!=str:
        return(False)
    if type(user)!=str:
        return(False)
    if type(password)!=str:
        return(False)
    validtype=["http","https"]
    if not "://" in url:
        url="http://"+url
    dec=urllib.parse.urlparse(url)
    if dec.scheme not in validtype:
        write_log("getHttpPage","type of page: '"+dec.scheme+"' valid type: "+str(validtype))
        return(False)
    if "." not in dec.netloc:
        write_log("getHttpPage","Bad hostname: " + dec.netloc)
        return(False)
    if dec.scheme == "http":
        h2 = http.client.HTTPConnection(dec.netloc,timeout=50)
    elif dec.scheme=="https":
        h2 = http.client.HTTPSConnection(dec.netloc,timeout=50)
    request=dec.path
    if dec.query!="":
        request+="?"+dec.query
    h2.putrequest("GET",request)
    if user!="":
        authstr=user+":"+password
        authstring = base64.b64encode(authstr.encode("ascii")).decode("ascii").replace('\n', '')
        h2.putheader("AUTHORIZATION", "Basic " + authstring)
    h2.endheaders()
    hresponse = h2.getresponse()
    try:
        httpdata = hresponse.read().decode("ascii").splitlines()
    except:
        httpdata = []
    if hresponse.status == 200:
        return(True)
    else:
        return(False)

def getHttpPage(url,user="",password=""):
    if type(url)!=str:
        return []
    if type(user)!=str:
        return []
    if type(password)!=str:
        return []
    validtype=["http","https"]
    if not "://" in url:
        url="http://"+url
    dec=urllib.parse.urlparse(url)
    if dec.scheme not in validtype:
        write_log("getHttpPage","type of page: '"+dec.scheme+"' valid type: "+str(validtype))
        return []
    if "." not in dec.netloc:
        write_log("getHttpPage","Bad hostname: " + dec.netloc)
        return []
    if dec.scheme == "http":
        h2 = http.client.HTTPConnection(dec.netloc,timeout=50)
    elif dec.scheme=="https":
        h2 = http.client.HTTPSConnection(dec.netloc,timeout=50)
    #write_log("getHttpPage","decode " + str(dec))
    request=dec.path
    if dec.query!="":
        request+="?"+dec.query
    h2.putrequest("GET",request)
    if user!="":
        authstr=user+":"+password
        authstring = base64.b64encode(authstr.encode("ascii")).decode("ascii").replace('\n', '')
        h2.putheader("AUTHORIZATION", "Basic " + authstring)
    h2.endheaders()
    hresponse = h2.getresponse()
    try:
        httpdata = hresponse.read().decode("ascii").splitlines()
    except:
        httpdata = []
    if hresponse.status == 200:
        return httpdata
    write_log("getHttpPage","ERROR "+str(hresponse.status)+" : " + str(hresponse.reason))
    write_log("getHttpPage","  proto  : "+str(dec.scheme))
    write_log("getHttpPage","  host   : "+str(dec.netloc))
    write_log("getHttpPage","  request: "+str(request))
    return httpdata

def add_mail(stri):
    mailfile=os.getenv("mailfile",datadir+"/mail.txt")
    if not os.path.exists(mailfile):
        ffi=open(mailfile,"w")
        ffi.write("Activity repport from argawaen.net server\n")
        ffi.write("======\n\n")
        ffi.write(time.strftime("%Y %h %d %H:%M:%S")+"\n")
    else:
        ffi=open(mailfile,"a")
    ffi.write(stri+"\n")
    ffi.close()

def flush_mail():
    mailfile=os.getenv("mailfile",datadir+"/mail.txt")
    if os.path.exists(mailfile):
        os.remove(mailfile)

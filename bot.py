import sys
import socket
import string
import signal
import time
import re
import datetime
import dns.resolver
from threading import Thread
from config import *

def signal_handler(signal, frame):
    s.send("%sAAA Q :Exiting on signal %s\n" % (SRVID, signal))
    print("[WRITE]: %sAAA Q :Exiting on signal %s" % (SRVID, signal))
    s.send("%s SQ %s 0 :Exiting on signal %s\n" % (SRVID, SRVNAME, signal))
    print("[WRITE]: %s SQ %s 0 :Exiting on signal %s" % (SRVID, SRVNAME, signal))
    sys.exit(0)

def isIP(address):
    #Takes a string and returns a status if it matches
    #a ipv4 address
    # 0 = false / 1 = true
    ip = False
    try:
        if address[0].isdigit():
            octets = address.split('.')
            if len(octets) == 4:
                ipAddr = "".join(octets)
                if ipAddr.isdigit():
                #correct format
                    if (int(octets[0]) >= 0) and (int(octets[0]) <= 255):
                        if (int(octets[1]) >= 0) and (int(octets[1]) <= 255):
                            if (int(octets[2]) >= 0) and (int(octets[2]) <= 255):
                                if (int(octets[3]) >= 0) and (int(octets[3]) <= 255):
                                    ip = True
    except IndexError:
        pass
    return ip


def DNSBL(ip, nick):
    bll = ["tor.dan.me.uk", "rbl.efnetrbl.org", "dnsbl.proxybl.org", "dnsbl.dronebl.org", "tor.efnet.org"]
    if isIP(ip) is False:
        answers = dns.resolver.query(ip,'A')
        for server in answers:
            rawip = server
    else:
        rawip = ip

    rawip = str(rawip)
    newip = rawip.split(".")
    newip = newip[::-1]
    newip = '.'.join(newip)

    for blacklist in bll:
        newstring = newip + "." + blacklist
        try:
            answers = dns.resolver.query(newstring,'A')
            if answers != False:
                s.send("%s GL * +*@%s 259200 %d %d :AUTO Your IP is listed as being an infected drone, or otherwise not fit to join %s. [Detected %s]\n" % (SRVID, rawip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, blacklist))
                print("[WRITE][DNSBL_FOUND]: %s GL * +*@%s 259200 %d %d :AUTO Your IP is listed as being an infected drone, or otherwise not fit to join %s. [Detected %s]" % (SRVID, rawip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, blacklist))
                break
        except dns.resolver.NXDOMAIN:
            continue

    http_connect(ip)

def http_connect(ip):
    testhost = "blindsighttf2.com:80"
    ports = [80,81,1075,3128,4480,6588,7856,8000,8080,8081,8090,7033,8085,8095,8100,8105,8110,1039,1050,1080,1098,11055,1200,19991,3332,3382,35233,443,444,4471,4480,5000,5490,5634,5800,63000,63809,65506,6588,6654,6661,6663,6664,6665,6667,6668,7070,7868,808,8085,8082,8118,8888,9000,9090,9988]


signal.signal(signal.SIGINT, signal_handler)
s=socket.socket()
s.connect((HOST, PORT))
boot_time = int(time.time())

s.send("PASS %s\n" % (SRVPASS))
print("[WRITE]: PASS %s" % (SRVPASS))
s.send("SERVER %s %s %d %d J10 %s]]] :%s\n" % (SRVNAME, HOPS, boot_time, boot_time, SRVID, SRVDESC))
print("[WRITE]: SERVER %s %s %d %d J10 %s]]] :%s" % (SRVNAME, HOPS, boot_time, boot_time, SRVID, SRVDESC))
s.send("%s N ProxyServ 1 %d ProxyServ services.gamesurge.net +oik AAAAAA %sAAA :Proxy Monitor Service\n" % (SRVID, boot_time, SRVID))
print("[WRITE]: %s N ProxyServ 1 %d ProxyServ services.gamesurge.net +oik AAAAAA %sAAA :Proxy Monitor Service" % (SRVID, boot_time, SRVID))
s.send("%s B #proxy %d %sAAA:o\n" % (SRVID, int(time.time()), SRVID))
print("[WRITE]: %s B #proxy %d ADAAA:o" % (SRVID, int(time.time())))
s.send("%sAAA M #proxy +o %sAAA %d\n" % (SRVID, SRVID, int(time.time())))
print("[WRITE]: %sAAA M #proxy +o %sAAA %d" % (SRVID, SRVID, int(time.time())))
s.send("%s EB\n" % (SRVID))
print("[WRITE]: %s EB" % (SRVID))

readbuffer = ""
try:
    if uplinkid is False or uplinkid == "":
        uplinkid = ""
except NameError:
    uplinkid = ""
try:
    if uplinkname is False or uplinkname == "":
        uplinkname = ""
except NameError:
    uplinkname = ""
try:
    if userlist is False:
        userlist = []
except NameError:
        userlist = []
try:
    if complete is False:
        complete = 0
except NameError:
        complete = 0
while 1:
    readbuffer=readbuffer + s.recv(32768)
    temp=string.split(readbuffer, "\n")
    readbuffer=temp.pop()

    for line in temp:
        print "[READ]: " + line
        line=string.rstrip(line)
        line=string.split(line)

        # Get initial data from uplink #
        if(line[0] == "SERVER"):
            if uplinkid == line[6][:2]:
                print "[ERROR][FATAL]: Uplink ID matches POPM ID. Exiting\n"
                sys.exit(0)
            else:
                uplinkid = line[6][:2]
                uplinkname = line[1]

        # Create our user dictionary #
        if(line[1] == "N"):
            if(":" in line[8]):
                userlist.append([line[2], line[8].split(":")[0], line[11]])
                print "[INFO]: New userlist is " + str(userlist)

        # Acknowldge the netburst #
        if(line[0] == uplinkid and line[1] == "EB"):
            s.send("%s EA\n" % (SRVID))
            print("[WRITE]: %s EA" % (SRVID))
            complete = 1

        # Check for ID collisons #
        if(line[1] == "S"):
            if uplinkid == line[7][:2]:
                print("[ERROR][FATAL]: Server %s has same ID as POPM. Exiting\n" % (line[2]))
                sys.exit(0)

        # Keep alive stuff #
        if(line[0] == uplinkid and line[1] == "Z"):
            s.send("%s G :%s\n" % (SRVID, SRVNAME))
            print("[WRITE]: %s G :%s" % (SRVID, SRVNAME))
        if(line[0] == uplinkid and line[1] == "G"):
            s.send("%s Z %s %s 0 %s\n" % (SRVID, SRVNAME, line[2][1:], line[4]))
            print("[WRITE]: %s Z %s %s 0 %s" % (SRVID, SRVNAME, line[2][1:], line[4]))

        # If we were squit, then abandon ship #
        if(line[1] == "SQ" and line[2] == uplinkname):
            print"[ERROR][FATAL]: Recieved SQUIT from uplink. Exiting\n"
            sys.exit(0)

        # Get incomming connections #
        if(line[1] == "N" and complete == 1):
            DNSBL(line[6], line[2])
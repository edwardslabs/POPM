import sys
import socket
import string
import signal
import time
import re
import datetime
from threading import Thread
from config import *

def signal_handler(signal, frame):
    s.send("%sAAA Q :Exiting on signal %s\n" % (SRVID, signal))
    print("[WRITE]: %sAAA Q :Exiting on signal %s" % (SRVID, signal))
    s.send("%s SQ %s 0 :Exiting on signal %s\n" % (SRVID, SRVNAME, signal))
    print("[WRITE]: %s SQ %s 0 :Exiting on signal %s" % (SRVID, SRVNAME, signal))
    sys.exit(0)

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
s.send("%s B #proxy %d ADAAA:o\n" % (SRVID, int(time.time())))
print("[WRITE]: %s B #proxy %d ADAAA:o" % (SRVID, int(time.time())))
s.send("%s EB\n" % (SRVID))
print("[WRITE]: %s EB" % (SRVID))

readbuffer = ""
if uplinkid is False or uplinkid == "":
    uplinkid = ""
while 1:
    readbuffer=readbuffer + s.recv(1024)
    temp=string.split(readbuffer, "\n")
    readbuffer=temp.pop()

    for line in temp:
        print "[READ]: " + line
        line=string.rstrip(line)
        line=string.split(line)

        if(line[0] == "SERVER"):
            if uplinkid == line[6][:2]:
                print "[ERROR][FATAL]: Uplink ID matches POPM ID. Exiting\n"
                sys.exit(0)
            else:
                uplinkid = line[6][:2]

        if(line[1] == "S"):
            if uplinkid == line[7][:2]:
                print("[ERROR][FATAL]: Server %s has same ID as POPM. Exiting\n" % (line[2]))
                sys.exit(0)

        if(line[0] == uplinkid and line[1] == "Z"):
            s.send("%s G :%s\n" % (SRVID, SRVNAME))
            print("[WRITE]: %s G :%s" % (SRVID, SRVNAME))
        if(line[0] == uplinkid and line[1] == "G"):
            s.send("%s Z %s %s 0 %s\n" % (SRVID, SRVNAME, line[2][1:], line[4]))
            print("[WRITE]: %s Z %s %s 0 %s" % (SRVID, SRVNAME, line[2][1:], line[4]))

        if(line[0] == uplinkid and line[1] == "EB"):
            s.send("%s EA\n" % (SRVID))
            print("[WRITE]: %s EA" % (SRVID))
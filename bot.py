import sys
import socket
import string
import signal
import time
import re
import datetime
from threading import Thread
from config import *

def privmsg(target, data):
    size=len(data)
    if size > 400:
        n=400
        trun=[str(data)[i:i + n] for i in range(0, len(str(data)), n)]
        x=0
        for i in trun:
            if x == 0:
                i=str(i) + "..."
                s.send("PRIVMSG %s :%s\n" % (target, i))
                print("-->[SENDING]<-- PRIVMSG %s :%s" % (target, i))
                time.sleep(1)
            elif x >= 1:
                i="..." + str(i)
                s.send("PRIVMSG %s :%s\n" % (target, i))
                print("-->[SENDING]<-- PRIVMSG %s :%s" % (target, i))
                time.sleep(1)
            x += 1
    elif size > 300 and size <= 400:
        s.send("PRIVMSG %s :%s\n" % (target, data))
        print("-->[SENDING]<-- PRIVMSG %s :%s" % (target, data))
    elif size > 150 and size <= 300:
        s.send("PRIVMSG %s :%s\n" % (target, data))
        print("-->[SENDING]<-- PRIVMSG %s :%s" % (target, data))
    else:
        s.send("PRIVMSG %s :%s\n" % (target, data))
        print("-->[SENDING]<-- PRIVMSG %s :%s" % (target, data))

def signal_handler(signal, frame):
    s.send("AK SQ %s %d :Exiting on signal %s\n" % (SRVNAME, int(time.time()), signal))
    print("W: AK SQ %s %d :Exiting on signal %s" % (SRVNAME, int(time.time()), signal))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

s=socket.socket()
s.connect((HOST, PORT))

boot_time = int(time.time())

s.send("PASS %s\n" % (SRVPASS))
print("W: PASS %s" % (SRVPASS))
s.send("SERVER %s %s %d %d J10 %s %s :%s\n" % (SRVNAME, HOPS, boot_time, boot_time, SRVNUM, EXT, SRVDESC))
print("W: SERVER %s %s %d %d J10 %s %s :%s" % (SRVNAME, HOPS, boot_time, boot_time, SRVNUM, EXT, SRVDESC))

readbuffer = ""
while 1:
    readbuffer=readbuffer + s.recv(1024)
    temp=string.split(readbuffer, "\n")
    readbuffer=temp.pop()

    for line in temp:
        print line
        line=string.rstrip(line)
        line=string.split(line)
        if readbuffer.find(' PRIVMSG ') != -1:
            nick=readbuffer.split('!')[0][1:]
            channel=readbuffer.split(' PRIVMSG ')[-1].split(' :')[0]
            message=readbuffer.split(' %s')[-1].split(' :')[1]

        if(line[0] == "SERVER"):
            # This will be put in to a config file, just testing #
            s.send("AK N ProxyServ 1 %d ProxyServ services.gamesurge.net +oik AAAAAA PSCAA :Proxy Monitor Service\n" % (boot_time))
            print("W: AK N ProxyServ 1 %d ProxyServ services.gamesurge.net +oik AAAAAA PSCAA :Proxy Monitor Service" % (boot_time))
        if(line[0] == "PING"):
            s.send("PONG %s\r\n" % line[1])
        #if(line[0] == "AB" and line[1] == "N"):
        #    s.send("AK FA %s %s %s\n" % (line[11], line[5], line[9]))
        #    print("W: AK FA %s %s %s\n" % (line[11], line[5], line[9]))
        #if(line[0] == "AB" and line[1] == "B"):
        #    s.send("AK B %s %s %s %s" % (line[2], line[3], line[4], line[5]))
        #    print("W: AK B %s %s %s %s" % (line[2], line[3], line[4], line[5]))
        #if(line[0] == "AB" and line[1] == "EB"):
        #    s.send("AK EB\n")
        #    print("W: AK EB")
        #    s.send("AK EA\n")
        #    print("W: AK EA")

        if(line[0] == "AB" and line[1] == "Z"):
            s.send("AK G :%s\n" % (SRVNAME))
            print("W: AK G :%s" % (SRVNAME))
        if(line[0] == "AB" and line[1] == "G"):
            s.send("AK Z %s %s 0 %s\n" % (SRVNAME, line[2][1:], line[4]))
            print("W: AK Z %s %s 0 %s" % (SRVNAME, line[2][1:], line[4]))

        if(line[0] == "AB" and line[1] == "EB"):
            s.send("AK EA\n")
            print("W: AK EA")
            s.send("AK EB\n")
            print("W: AK EB")
            #s.send("AK B #support %s +tn\n" % (str(time.time())))
            #print("AK B #support %s +tn" % (str(time.time())))
            
        if(line[0] == "AB" and line[1] == "B" and line[2] == "#proxy"):
            s.send("AK B #proxy %d PSCAA:o\n" % ((int(time.time()))))
            print("W: AK B #proxy %d PSCAA:o" % ((int(time.time()))))
        if(line[1] == "001"):
            idandjoin()
            thread = Thread(target=startloop)
            thread.start()
            thread = Thread(target=reconnectloop)
            thread.start()
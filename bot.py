import sys
import socket
import ssl
import string
import signal
import time
import re
import datetime
import dns.resolver
import httplib
from threading import Thread
from thread import start_new_thread, allocate_lock
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
    if ENABLE_DNSBL == 0:
        http_connect(ip)
    else:
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

num_threads = 0
thread_started = False
lock = allocate_lock()
contrue = 0
def http_connect(ip):
    if ENABLE_HTTP == 0:
        sockscheck(ip, port)
    else:
        global num_threads, thread_started, contrue
        testhost = "blindsighttf2.com:80"
        ports = [80,81,1075,3128,4480,6588,7856,8000,8080,8081,8090,7033,8085,8095,8100,8105,8110,1039,1050,1080,1098,11055,1200,19991,3332,3382,35233,443,444,4471,4480,5000,5490,5634,5800,63000,63809,65506,6588,6654,6661,6663,6664,6665,6667,6668,7070,7868,808,8085,8082,8118,8888,9000,9090,9988]

        def http_connect_threads(ip, port):
            global num_threads, thread_started, contrue
            lock.acquire()
            num_threads += 1
            thread_started = True
            lock.release()
            tcp=socket.socket()
            tcp.settimeout(2)
            portbuf = ""
            try:
                tcp.connect((ip, port))
                tcp.send("CONNECT %s HTTP/1.0\r\n\r\n" % (ip))
                #print "[~~~MADE IT PAST TRY~~~]"
                inttime1 = int(time.time())
                inttime2 = int(time.time())
                while inttime2 - inttime1 < 2:
                    inttime2 = int(time.time())
                    data = tcp.recv(1024)
                    if data is not False and "HTTP/1.0 200 OK" in data:
                        s.send("%s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]\n" % (SRVID, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
                        print("[WRITE][HTTP_CONNECT]: %s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]" % (SRVID, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
                        contrue += 1
                        tcp.close()
                        break
            except socket.error, v:
                #print "[CONNERR (%s) %s]" % (port, v)
                pass
            lock.acquire()
            num_threads -= 1
            lock.release()

        def https_connect_threads(ip, port):
            global num_threads, thread_started, contrue
            lock.acquire()
            num_threads += 1
            thread_started = True
            lock.release()

            tcps=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ssl_sock = ssl.wrap_socket(tcps)

            ssl_sock.settimeout(2)
            portbuf = ""
            try:
                ssl_sock.connect((ip, port))
                ssl_sock.send("CONNECT %s HTTP/1.0\r\n\r\n" % (ip))
                #print "[~~~SSL MADE IT PAST TRY~~~]"
                inttime1 = int(time.time())
                inttime2 = int(time.time())
                while inttime2 - inttime1 < 2:
                    inttime2 = int(time.time())
                    data = ssl_sock.recv(1024)
                    if data is not False and "HTTP/1.0 200 OK" in data:
                        s.send("%s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]\n" % (SRVID, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
                        print("[WRITE][HTTP_CONNECT]: %s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]" % (SRVID, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
                        contrue += 1
                        ssl_sock.close()
                        break
            except socket.error, v:
                #print "[SSL CONNERR (%s) %s]" % (port, v)
                pass
            lock.acquire()
            num_threads -= 1
            lock.release()

        for newport in ports:
            start_new_thread(http_connect_threads, (ip, newport, ))
            start_new_thread(https_connect_threads, (ip, newport, ))

        while not thread_started:
            pass
        while num_threads > 0:
            pass

        if str(contrue) == "0" or contrue is None:
            sockscheck(ip)

def sockscheck(ip):
    if ENABLE_SOCKS != 0:
        global num_threads, thread_started, contrue
        ports = [1080,1075,10000,10080,10099,10130,10242,10777,1025,1026,1027,1028,1029,1030,1031,1032,1033,1039,1050,1066,1081,1098,11011,11022,11033,11055,11171,1122,11225,1180,1182,1200,1202,1212,1234,12654,1337,14841,16591,17327,1813,18888,1978,1979,19991,2000,21421,22277,2280,24971,24973,25552,25839,26905,28882,29992,3127,3128,32167,3330,3380,34610,3801,3867,40,4044,41080,41379,43073,43341,443,44548,4471,43371,44765,4914,49699,5353,559,58,6000,62385,63808,6551,6561,6664,6748,6969,7007,7080,8002,8009,8020,8080,8085,8111,8278,8751,8888,9090,9100,9988,9999,59175,5001,19794]

        def check_socks(ip, port):
            global num_threads, thread_started, contrue
            lock.acquire()
            num_threads += 1
            thread_started = True
            lock.release()

            check=httplib.HTTPConnection('google.com', port, ip, timeout=1)
            try:
                check.connect()
                if check != False:
                    s.send("%s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected socks/%s]\n" % (SRVID, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
                    print("[WRITE][SOCKS]: %s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected socks/%s]" % (SRVID, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
                    contrue += 1
                    check.close()
            except socket.error, v:
                pass

            lock.acquire()
            num_threads -= 1
            lock.release()

        for newport in ports:
            start_new_thread(check_socks, (ip, newport, ))

        while not thread_started:
            pass
        while num_threads > 0:
            pass

signal.signal(signal.SIGINT, signal_handler)
s=socket.socket()
s.connect((HOST, PORT))
boot_time = int(time.time())

s.send("PASS %s\n" % (SRVPASS))
print("[WRITE]: PASS %s" % (SRVPASS))
s.send("SERVER %s %s %d %d J10 %s]]] :%s\n" % (SRVNAME, HOPS, boot_time, boot_time, SRVID, SRVDESC))
print("[WRITE]: SERVER %s %s %d %d J10 %s]]] :%s" % (SRVNAME, HOPS, boot_time, boot_time, SRVID, SRVDESC))
s.send("%s N %s 1 %d %s services.gamesurge.net +oik AAAAAA %sAAA :Proxy Monitor Service\n" % (SRVID, BOT_NAME, boot_time, BOT_NAME, SRVID))
print("[WRITE]: %s N %s 1 %d %s services.gamesurge.net +oik AAAAAA %sAAA :Proxy Monitor Service" % (SRVID, BOT_NAME, boot_time, SRVID, BOT_NAME))
s.send("%s B %s %d %sAAA:o\n" % (SRVID, DEBUG_CHANNEL, int(time.time()), SRVID))
print("[WRITE]: %s B %s %d %sAAA:o" % (SRVID, DEBUG_CHANNEL, int(time.time()), SRVID))
s.send("%sAAA M %s +o %sAAA %d\n" % (SRVID, DEBUG_CHANNEL, SRVID, int(time.time())))
print("[WRITE]: %sAAA M %s +o %sAAA %d" % (SRVID, DEBUG_CHANNEL, SRVID, int(time.time())))
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
            thread = Thread(target=DNSBL(line[6], line[2]))
            thread.start()

        # Test stuff #
        if(any(line[0] in i for i in userlist) is True and line[1] == "P" and line[2][:1] == "#"):
            if(line[3] == ":.threads"):
                try:
                    s.send("%sAAA P %s :There are %s threads running\n" % (SRVID, line[2], threading.activeCount()))
                    print("[WRITE]: %sAAA P %s :There are %s threads running" % (SRVID, line[2], threading.activeCount()))
                except NameError:
                    s.send("%sAAA P %s :There are no threads running\n" % (SRVID, line[2]))
                    print("[WRITE]: %sAAA P %s :There are no threads running" % (SRVID, line[2]))
            elif(line[3] == ":.help"):
                s.send("%sAAA O %s :-=-=-=-=-=-= %s Help -=-=-=-=-=-=\n" % (SRVID, line[0], BOT_NAME))
                s.send("%sAAA O %s :No information available at this time.\n" % (SRVID, line[0]))
                s.send("%sAAA O %s :-=-=-=-=-=-= End Of Help -=-=-=-=-=-=\n" % (SRVID, line[0]))
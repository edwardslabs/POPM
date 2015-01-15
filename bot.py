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
import psycopg2
from threading import Thread
from thread import start_new_thread, allocate_lock
from config import *

def signal_handler(signal, frame):
    s.send("%sAAA Q :Exiting on signal %s\n" % (SERVER_NUMERIC, signal))
    print("[WRITE]: %sAAA Q :Exiting on signal %s" % (SERVER_NUMERIC, signal))
    s.send("%s SQ %s 0 :Exiting on signal %s\n" % (SERVER_NUMERIC, SERVER_HOST_NAME, signal))
    print("[WRITE]: %s SQ %s 0 :Exiting on signal %s" % (SERVER_NUMERIC, SERVER_HOST_NAME, signal))
    sys.exit(0)

def show_access(target, source):
    if target == "*":
        cur.execute("SELECT access,admin FROM users")
        s.send("%sAAA O %s :Account    Level\n" % (SERVER_NUMERIC, source))
        num = 0
        for row in cur.fetchall():
            s.send("%sAAA O %s :%s  %s\n" % (SERVER_NUMERIC, source, row[1], row[0]))
            num += 1
        s.send("%sAAA O %s :Found %d matches.\n" % (SERVER_NUMERIC, source, num))
    else:
        cur.execute("SELECT access,admin FROM users WHERE admin = %r" % (target))
        if cur.rowcount < 1:
            s.send("%sAAA O %s :Could not find account %s.\n" % (SERVER_NUMERIC, source, target))
        else:
            for row in cur.fetchall():
                account = row[1]
                access = row[0]
            s.send("%sAAA O %s :Account %s has access %d.\n" % (SERVER_NUMERIC, source, account, access))

def get_level_req(param):
    if param == "access_set":
        cur.execute("SELECT access_set FROM settings")
        level = 0
        for row in cur.fetchall():
            level = row[0]
        return level
    elif param == "setters":
        cur.execute("SELECT access_set FROM settings")
        level = 0
        for row in cur.fetchall():
            level = row[0]
        return level

def is_settable(param):
    if param.lower() == "dnsbl" or param.lower() == "http" or param.lower() == "socks" or param.lower() == "die" or param.lower() == "set" or param.lower() == "setters" or param.lower() == "http_connect":
        return True
    return False

def get_set(target):
    cur.execute("SELECT enable_dnsbl,enable_http,enable_socks,access_die,access_set FROM settings")
    s.send("%sAAA O %s :Current configuration settings:\n" % (SERVER_NUMERIC, target))
    for row in cur.fetchall():
        s.send("%sAAA O %s :DNSBL Scans:                   %s\n" % (SERVER_NUMERIC, target, row[0]))
        s.send("%sAAA O %s :HTTP_CONNECT Scans:     %s\n" % (SERVER_NUMERIC, target, row[1]))
        s.send("%sAAA O %s :SOCKS Scans:                   %s\n" % (SERVER_NUMERIC, target, row[2]))
        s.send("%sAAA O %s :Die access:                        %s\n" % (SERVER_NUMERIC, target, row[3]))
        s.send("%sAAA O %s :Setters level:                     %s\n" % (SERVER_NUMERIC, target, row[4]))
    s.send("%sAAA O %s :End of configuration.\n" % (SERVER_NUMERIC, target))

def update_settings(param, newlevel, target):
    newlevel = int(newlevel)
    if param == "dnsbl":
        param = "enable_dnsbl"
        fancy = "DNSBL Scans"
    elif param == "http" or param == "http_connect":
        param = "enable_http"
        fancy = "HTTP_CONNECT Scans"
    elif param == "socks":
        param = "enable_socks"
        fancy = "SOCKS Scans"
    elif param == "die":
        param = "access_die"
        fancy = "Die access"
    elif param == "set" or param == "setters":
        param = "access_set"
        fancy = "Setters"

    if param == "enable_dnsbl" or param == "enable_socks" or param == "enable_http":
        if newlevel > 1 or newlevel < 0:
            s.send("%sAAA O %s :%s must be either ON or OFF.\n" % (SERVER_NUMERIC, target, fancy))
        else:
             if newlevel == 1:
                 newlevel = True
                 fancyonoff = "on"
             else:
                 newlevel = False
                 fancyonoff = "off"
             cur.execute("UPDATE settings SET %s = %s" % (param, newlevel))
             pgconn.commit()
             print "Updated settings"
             s.send("%sAAA O %s :%s has been set to %s.\n" % (SERVER_NUMERIC, target, fancy, fancyonoff))
    else:
         cur.execute("UPDATE settings SET %s = %d" % (param, newlevel))
         pgconn.commit()
         print "Updated settings"
         s.send("%sAAA O %s :%s has been set to %s\n" % (SERVER_NUMERIC, target, fancy, newlevel))


def get_set_value(param, target):
    if param == "dnsbl":
        param = "enable_dnsbl"
        fancy = "DNSBL Scans"
    elif param == "http" or param == "http_connect":
        param = "enable_http"
        fancy = "HTTP_CONNECT Scans"
    elif param == "socks":
        param = "enable_socks"
        fancy = "SOCKS Scans"
    elif param == "die":
        param = "access_die"
        fancy = "Die access"
    elif param == "set" or param == "setters":
        param = "access_set"
        fancy = "Setters"
    cur.execute("SELECT %s FROM settings" % (param))
    for row in cur.fetchall():
        s.send("%sAAA O %s :%s is set to %s\n" % (SERVER_NUMERIC, target, fancy, row[0]))


def update_access(user, level, whodidit):
    if isinstance(level, int):
        bywho = get_acc(whodidit)
        cur.execute("SELECT admin FROM users WHERE admin = %r" % (user))
        epoch = int(time.time())
        if cur.rowcount < 1:
            if level < 0:
                s.send("%sAAA O %s :Account %s does not exist.\n" % (SERVER_NUMERIC, whodidit, user))
            else:
                cur.execute("INSERT INTO users (admin,access,added,bywho) VALUES (%r, %r, %r, %r)" % (user, level, epoch, bywho))
                pgconn.commit()
                s.send("%sAAA O %s :Account %s has been added with access %d.\n" % (SERVER_NUMERIC, whodidit, user, level))
        else:
            if level < 0:
                cur.execute("DELETE FROM users * WHERE admin = %r" % (user))
                pgconn.commit()
                s.send("%sAAA O %s :Access for account %s has been deleted.\n" % (SERVER_NUMERIC, whodidit, user))
            else:
                cur.execute("UPDATE users SET access = %r, bywho = %r, added = %r WHERE admin = %r" % (level, bywho, epoch, user))
                pgconn.commit()
                s.send("%sAAA O %s :Account %s has been updated to access %d.\n" % (SERVER_NUMERIC, whodidit, user, level))
    else:
        s.send("%sAAA O %s :Access levels must be an integer.\n" % (SERVER_NUMERIC, whodidit))

def get_acc(numnick):
    authed = 0
    access = 0
    for i in userlist:
        account = i.split(":")[0]
        ircnum = i.split(":")[1]
        if ircnum == numnick:
            return account

def access_level(numnick):
    authed = 0
    access = 0
    for i in userlist:
        account = i.split(":")[0]
        ircnum = i.split(":")[1]
        if ircnum == numnick:
            authed += 1

    if authed == 0:
        s.send("%sAAA O %s :You must first authenticate with NickServ.\n" % (SERVER_NUMERIC, numnick))
    else:
        cur.execute("SELECT access FROM users WHERE admin = %r" % (account))
        is_user = 0
        for row in cur.fetchall():
            access = row[0]
            is_user += 1
        if is_user > 0:
            return access
        else:
            s.send("%sAAA O %s :You must first authenticate with NickServ.\n" % (SERVER_NUMERIC, numnick))
            return False

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
                    s.send("%s GL * +*@%s 259200 %d %d :AUTO Your IP is listed as being an infected drone, or otherwise not fit to join %s. [Detected %s]\n" % (SERVER_NUMERIC, rawip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, blacklist))
                    print("[WRITE][DNSBL_FOUND]: %s GL * +*@%s 259200 %d %d :AUTO Your IP is listed as being an infected drone, or otherwise not fit to join %s. [Detected %s]" % (SERVER_NUMERIC, rawip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, blacklist))
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
                        s.send("%s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]\n" % (SERVER_NUMERIC, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
                        print("[WRITE][HTTP_CONNECT]: %s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]" % (SERVER_NUMERIC, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
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
                        s.send("%s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]\n" % (SERVER_NUMERIC, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
                        print("[WRITE][HTTP_CONNECT]: %s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]" % (SERVER_NUMERIC, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
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
                    s.send("%s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected socks/%s]\n" % (SERVER_NUMERIC, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
                    print("[WRITE][SOCKS]: %s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected socks/%s]" % (SERVER_NUMERIC, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
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

pgconn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
cur = pgconn.cursor()

# Have cursor dedicated for settings look ups #
pgconnauto = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
curauto = pgconnauto.cursor()

curauto.execute("SELECT enable_dnsbl,enable_http,enable_socks,access_die,access_set FROM settings")
for row in curauto.fetchall():
    ENABLE_DNSBL = row[0]
    ENABLE_HTTP = row[1]
    ENABLE_SOCKS = row[2]
    ACCESS_DIE = row[3]
    ACCESS_SET = row[4]

signal.signal(signal.SIGINT, signal_handler)
s=socket.socket()
s.connect((HOST, PORT))
boot_time = int(time.time())

s.send("PASS %s\n" % (SERVER_PASS))
print("[WRITE]: PASS %s" % (SERVER_PASS))
s.send("SERVER %s %s %d %d J10 %s]]] :%s\n" % (SERVER_HOST_NAME, HOPS, boot_time, boot_time, SERVER_NUMERIC, SERVER_DESCRIPTION))
print("[WRITE]: SERVER %s %s %d %d J10 %s]]] :%s" % (SERVER_HOST_NAME, HOPS, boot_time, boot_time, SERVER_NUMERIC, SERVER_DESCRIPTION))
s.send("%s N %s 1 %d %s %s %s AAAAAA %sAAA :%s\n" % (SERVER_NUMERIC, BOT_NAME, boot_time, BOT_NAME, BOT_HOST, BOT_MODE, SERVER_NUMERIC, BOT_DESC))
print("[WRITE]: %s N %s 1 %d %s %s %s AAAAAA %sAAA :%s" % (SERVER_NUMERIC, BOT_NAME, boot_time, SERVER_NUMERIC, BOT_HOST, BOT_MODE, BOT_NAME, BOT_DESC))
s.send("%s B %s %d %sAAA:o\n" % (SERVER_NUMERIC, DEBUG_CHANNEL, int(time.time()), SERVER_NUMERIC))
print("[WRITE]: %s B %s %d %sAAA:o" % (SERVER_NUMERIC, DEBUG_CHANNEL, int(time.time()), SERVER_NUMERIC))
s.send("%sAAA M %s +o %sAAA %d\n" % (SERVER_NUMERIC, DEBUG_CHANNEL, SERVER_NUMERIC, int(time.time()))) # Unless our server is U-Lined, this won't work #
print("[WRITE]: %sAAA M %s +o %sAAA %d" % (SERVER_NUMERIC, DEBUG_CHANNEL, SERVER_NUMERIC, int(time.time())))
s.send("%s EB\n" % (SERVER_NUMERIC))
print("[WRITE]: %s EB" % (SERVER_NUMERIC))

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
                userlist.append("%s:%s" % (line[8].split(":")[0], line[11]))
                print "[INFO]: New userlist is " + str(userlist)

        # Add users as they authenticate #
        if(line[1] == "AC"):
            userlist.append("%s:%s" % (line[3], line[2]))
            print "[INFO]: New userlist is " + str(userlist)

        # Acknowldge the netburst #
        if(line[0] == uplinkid and line[1] == "EB"):
            s.send("%s EA\n" % (SERVER_NUMERIC))
            print("[WRITE]: %s EA" % (SERVER_NUMERIC))
            complete = 1

        # Check for ID collisons #
        if(line[1] == "S"):
            if uplinkid == line[7][:2]:
                print("[ERROR][FATAL]: Server %s has same ID as POPM. Exiting\n" % (line[2]))
                sys.exit(0)

        # Keep alive stuff #
        if(line[0] == uplinkid and line[1] == "Z"):
            s.send("%s G :%s\n" % (SERVER_NUMERIC, SERVER_HOST_NAME))
            print("[WRITE]: %s G :%s" % (SERVER_NUMERIC, SERVER_HOST_NAME))
        if(line[0] == uplinkid and line[1] == "G"):
            s.send("%s Z %s %s 0 %s\n" % (SERVER_NUMERIC, SERVER_HOST_NAME, line[2][1:], line[4]))
            print("[WRITE]: %s Z %s %s 0 %s" % (SERVER_NUMERIC, SERVER_HOST_NAME, line[2][1:], line[4]))

        # If we were squit, then abandon ship #
        if(line[1] == "SQ" and line[2] == uplinkname):
            print"[ERROR][FATAL]: Recieved SQUIT from uplink. Exiting\n"
            sys.exit(0)

        # Get incomming connections #
        if(line[1] == "N" and complete == 1):
            thread = Thread(target=DNSBL(line[6], line[2]))
            thread.start()

        # Commands (efficienize me) #
        if(line[1] == "P" and line[2][:1] == "#" or line[1] == "P" and line[2] == "%sAAA" % (SERVER_NUMERIC)):
            channel = False
            target = line[0]
            if line[2][:1] == "#":
                channel = True
                channel_target = line[2]
                target = line[0]
            if(line[3].lower() == ":.threads" and channel is True or channel is False and line[3].lower() == ":threads"):
                if access_level(target) > 750:
                    try:
                        s.send("%sAAA O %s :There are %s threads running\n" % (SERVER_NUMERIC, target, threading.activeCount()))
                        print("[WRITE]: %sAAA O %s :There are %s threads running" % (SERVER_NUMERIC, target, threading.activeCount()))
                    except NameError:
                        s.send("%sAAA O %s :There are no threads running\n" % (SERVER_NUMERIC, target))
                        print("[WRITE]: %sAAA O %s :There are no threads running" % (SERVER_NUMERIC, target))
                elif access_level(target) <= 749:
                    s.send("%sAAA O %s :You lack access to this command\n" % (SERVER_NUMERIC, target))
                    print("[WRITE]: %sAAA O %s :You lack access to this command" % (SERVER_NUMERIC, target))
            elif(line[3].lower() == ":.help" and channel is True or channel is False and line[3].lower() == ":help"):
                if access_level(target) > 0:
                    try:
                        if line[4] != False:
                            if line[4].lower() == "threads":
                                s.send("%sAAA O %s :-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :THREADS displays the current number of worker threads by %s.\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :These threads are spawned when an incoming connection is recieved\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :to check for proxys on the remote host.\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-\n" % (SERVER_NUMERIC, target))
                            elif line[4].lower() == "access":
                                s.send("%sAAA O %s :-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :ACCESS is a multi-functional command. Access has the ability to\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :check your access with %s, check other's access, add other users to %s\n" % (SERVER_NUMERIC, target, BOT_NAME, BOT_NAME))
                                s.send("%sAAA O %s :and to remove users access to %s. At this time, only root users may\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :add or remove other users from %s.\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :Note: To remove a users access, set their access to -1\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :Examples:\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :/msg %s ACCESS foobar\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :/msg %s ACCESS *\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :/msg %s ACCESS foo 950\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :/msg %s ACCESS bar -1\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-\n" % (SERVER_NUMERIC, target))
                            elif line[4].lower() == "die":
                                s.send("%sAAA O %s :-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :DIE causes %s to quit and POPM to disconnect from %s.\n" % (SERVER_NUMERIC, target, BOT_NAME, NETWORK_NAME))
                                s.send("%sAAA O %s :This will completly stop the program and will have to\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :be restarted locally. DIE takes arguments for the QUIT message\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :and SQUIT reason. Note: When you use DIE, your :NickServ account\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :name will be attached to the SQUIT message.\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-\n" % (SERVER_NUMERIC, target))
                            else:
                                s.send("%sAAA O %s :%s is an unknown command to me.\n" % (SERVER_NUMERIC, target, line[4]))
                    except IndexError:
                        if access_level(target) > 0:
                            s.send("%sAAA O %s :-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-\n" % (SERVER_NUMERIC, target, BOT_NAME))
                            s.send("%sAAA O %s :%s gives authorized users extra control over the proxy monitoring system.\n" % (SERVER_NUMERIC, target, BOT_NAME))
                            s.send("%sAAA O %s :General commands:\n" % (SERVER_NUMERIC, target))
                            s.send("%sAAA O %s :Threads:        Shows current number of threads\n" % (SERVER_NUMERIC, target))
                            s.send("%sAAA O %s :Access:         Shows access for accounts\n" % (SERVER_NUMERIC, target))
                            s.send("%sAAA O %s :Set:            Sets the configuration for POPM\n" % (SERVER_NUMERIC, target))
                            s.send("%sAAA O %s :Die:            Terminates POPM and disconnects from %s\n" % (SERVER_NUMERIC, target, NETWORK_NAME))
                            s.send("%sAAA O %s :-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-\n" % (SERVER_NUMERIC, target))
            elif(line[3].lower() == ":.access" and channel is True or channel is False and line[3].lower() == ":access"):
                try:
                    if line[5] != False:
                        try:
                            access = line[5]
                            access = int(access)
                        except ValueError:
                            s.send("%sAAA O %s :Access level must be an integer.\n" % (SERVER_NUMERIC, target))
                            break
                        if access_level(target) == 1000:
                            if access <= 1000:
                                update_access(line[4], access, target)
                            else:
                                s.send("%sAAA O %s :Access must be greater than 1000\n" % (SERVER_NUMERIC, target))
                        else:
                            s.send("%sAAA O %s :Access modification can only be done via root (1000 access) users.\n" % (SERVER_NUMERIC, target))
                except IndexError:
                    try:
                        if line[4] != False:
                            if access_level(target) > 0:
                                show_access(line[4], target)
                    except IndexError:
                        if access_level(target) > 0:
                            s.send("%sAAA O %s :Account %s has access %s.\n" % (SERVER_NUMERIC, target, get_acc(target), access_level(target)))
            elif(line[3].lower() == ":.die" and channel is True or channel is False and line[3].lower() == ":die"):
                try:
                    if line[4] != False:
                        arlen = len(line)
                        newstring = ""
                        i = 4
                        while i < arlen:
                            if newstring == "":
                                newstring = line[i]
                            else:
                                newstring = newstring + " " + line[i]
                            i += 1
                        account = get_acc(target)
                        if access_level(target) >= 900:
                            s.send("%sAAA Q :%s\n" % (SERVER_NUMERIC, newstring))
                            print("[WRITE]: %sAAA Q :%s" % (SERVER_NUMERIC, newstring))
                            s.send("%s SQ %s 0 :[%s (by %s)]\n" % (SERVER_NUMERIC, SERVER_HOST_NAME, newstring, account))
                            print("[WRITE]: %s SQ %s 0 :[%s (by %s)]" % (SERVER_NUMERIC, SERVER_HOST_NAME, newstring, account))
                            sys.exit(0)
                        else:
                            s.send("%sAAA O %s :You lack access to this command\n" % (SERVER_NUMERIC, target))
                            print("[WRITE]: %sAAA O %s :You lack access to this command" % (SERVER_NUMERIC, target))
                except IndexError:
                    s.send("%sAAA O %s :Insufficient paramaters for DIE\n" % (SERVER_NUMERIC, target))
                    print("[WRITE]: %sAAA O %s :Insufficient paramaters for DIE" % (SERVER_NUMERIC, target))
            elif(line[3].lower() == ":.set" and channel is True or channel is False and line[3].lower() == ":set"):
                try:
                    if line[4] != False:
                        if access_level(target) >= get_level_req("access_set"):
                            if is_settable(line[4]) is True:
                                try:
                                    if line[5] != False:
                                        try:
                                            newlevel = line[5]
                                            if newlevel.lower() == "on":
                                                newlevel = 1
                                            elif newlevel.lower() == "off":
                                                newlevel = 0
                                            else:
                                                newlevel = int(newlevel)
                                        except ValueError:
                                            s.send("%sAAA O %s :Paramater must be an integer.\n" % (SERVER_NUMERIC, target))
                                        if newlevel <= 1000 and newlevel >= 0:
                                            update_settings(line[4], newlevel, target)
                                        else:
                                            s.send("%sAAA O %s :Paramater must be an integer between 0 and 1000\n" % (SERVER_NUMERIC, target))
                                except IndexError:
                                    get_set_value(line[4], target)
                            else:
                                s.send("%sAAA O %s :Invalid SET option.\n" % (SERVER_NUMERIC, target))
                        else:
                            s.send("%sAAA O %s :Insufficient access.\n" % (SERVER_NUMERIC, target))
                except IndexError:
                    if access_level(target) >= get_level_req("setters"):
                        get_set(target)

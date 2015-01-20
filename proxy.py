import sys
import socket
import socks
import ssl
import string
import time
import dns.resolver
import config
from multiprocessing import Process
global config
global Process

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
    from settings import get_dnsl_value
    bll = ["tor.dan.me.uk", "rbl.efnetrbl.org", "dnsbl.proxybl.org", "dnsbl.dronebl.org", "tor.efnet.org"]
    try:
        if isIP(ip) is False:
            answers = dns.resolver.query(ip,'A')
            for server in answers:
                rawip = server
        else:
            rawip = ip
    except dns.resolver.NXDOMAIN:
        rawip = ip

    rawip = str(rawip)

    if get_dnsl_value() == 0:
        http_connect(rawip)
    else:
        print "[SCANNING]: DNSBL scan on " + str(rawip)
        newip = rawip.split(".")
        newip = newip[::-1]
        newip = '.'.join(newip)
        contrue = 0
        for blacklist in bll:
            newstring = newip + "." + blacklist
            try:
                answers = dns.resolver.query(newstring,'A')
                if answers != False:
                    gline_dnsbl(ip, int(time.time()), int(time.time()) + config.DURATION, blacklist)
                    contrue = 0
                    break
            except dns.resolver.NXDOMAIN:
                contrue += 1
                continue

        if contrue == 5:
            http_connect(rawip)

def http_connect_threads(ip, port):
    from commands import gline_http
    global tested, contrue
    tcp=socket.socket()
    tcp.settimeout(2)
    portbuf = ""
    try:
        tcp.connect((ip, port))
        tcp.send("CONNECT %s HTTP/1.0\r\n\r\n" % (ip))
        inttime1 = int(time.time())
        inttime2 = int(time.time())
        while inttime2 - inttime1 < 2:
            inttime2 = int(time.time())
            data = tcp.recv(1024)
            if data is not False and "HTTP/1.0 200 OK" in data:
                gline_http(ip, int(time.time()), int(time.time()) + config.DURATION, port)
                tcp.close()
                break
    except socket.error, v:
        pass

def https_connect_threads(ip, port):
    from commands import gline_http
    global tested, contrue
    tcps=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = ssl.wrap_socket(tcps)
    ssl_sock.settimeout(2)
    portbuf = ""
    try:
        ssl_sock.connect((ip, port))
        ssl_sock.send("CONNECT %s HTTP/1.0\r\n\r\n" % (ip))
        inttime1 = int(time.time())
        inttime2 = int(time.time())
        while inttime2 - inttime1 < 2:
            inttime2 = int(time.time())
            data = ssl_sock.recv(1024)
            if data is not False and "HTTP/1.0 200 OK" in data:
                gline_http(ip, int(time.time()), int(time.time()) + config.DURATION, port)
                ssl_sock.close()
                break
    except socket.error, v:
        pass

def http_connect(ip):
    from commands import gline_http
    from settings import get_http_value
    global tested
    if get_http_value() == 0:
        sockscheck(ip)
    else:
        global num_threads, thread_started, contrue
        testhost = "blindsighttf2.com:80"
        print "[SCANNING]: HTTP Connect on " + str(ip)
        ports = [80,81,1075,3128,4480,6588,7856,8000,8080,8081,8090,7033,8085,8095,8100,8105,8110,1039,1050,1080,1098,11055,1200,19991,3332,3382,35233,443,444,4471,4480,5000,5490,5634,5800,63000,63809,65506,6588,6654,6661,6663,6664,6665,6667,6668,7070,7868,808,8085,8082,8118,8888,9000,9090,9988]

        for newport in ports:
            http = Process(target=http_connect_threads, args=(ip, newport))
            http.start()
            http = Process(target=https_connect_threads, args=(ip, newport))
            http.start()

        sockscheck(ip)

def sockscheck(ip):
    from settings import get_socks_value
    if get_socks_value() != 0:
        ports = [1080,1075,10000,10080,10099,10130,10242,10777,1025,1026,1027,1028,1029,1030,1031,1032,1033,1039,1050,1066,1081,1098,11011,11022,11033,11055,11171,1122,11225,1180,1182,1200,1202,1212,1234,12654,1337,14841,16591,17327,1813,18888,1978,1979,19991,2000,21421,22277,2280,24971,24973,25552,25839,26905,28882,29992,3127,3128,32167,3330,3380,34610,3801,3867,40,4044,41080,41379,43073,43341,443,44548,4471,43371,44765,4914,49699,5353,559,58,6000,62385,63808,6551,6561,6664,6748,6969,7007,7080,8002,8009,8020,8080,8085,8111,8278,8751,8888,9090,9100,9988,9999,59175,5001,19794]

        def check_socks(ip, port):
            print "[SCANNING]: SOCKS testing " + str(port)
            try:
                sen = struct.pack('BBB', 0x05, 0x01, 0x00)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect(( ip , int( port )  ))
                s.sendall(sen)
                data = s.recv(2)
                s.close()
                version, auth = struct.unpack('BB', data)
                print 'server : port  is  ', ip, ':', port, '; varsion: ', version
            except Exception as e:
                print e
                #print "Port " + str(port) + " is dead"
                pass

        for newport in ports:
            socksc = Process(target=check_socks, args=(ip, newport))
            socksc.start()

        return
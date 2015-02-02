import config
import dns.resolver
from multiprocessing import Process
import socket
import ssl
from stats import update_ban
import string
from struct import *
import sys
import time
global config
global pack
global Process

def isIPv6(address):
    import re
    pattern = r'^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$'
    if re.match(pattern, address):
        return True
    else:
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

def getTrueIP(ip):
    ip = str(ip)
    if isIP(ip) is False and isIPv6(ip) is False:
        try:
            answers = dns.resolver.query(ip,'A')
            answers.timeout = 2
            answers.lifetime = 2
            for server in answers:
                rawip = server
            return rawip
        except dns.resolver.NXDOMAIN:
            return ip
        except dns.exception.Timeout:
            try:
                answers = dns.resolver.query(ip,'AAAA')
                answers.timeout = 2
                answers.lifetime = 2
                for server in answers:
                    rawip = server
                return rawip
            except dns.resolver.NXDOMAIN:
                return ip
            except dns.exception.Timeout:
                return ip
    else:
        return ip

def DNSBL(ip, nick, DNSTRUE, HTTPTRUE, SOCKSTRUE, uniquehash):
    bll = ["tor.dan.me.uk", "rbl.efnetrbl.org", "dnsbl.proxybl.org", "dnsbl.dronebl.org", "tor.efnet.org"]
    if DNSTRUE == 0 or isIPv6(ip):
        http_connect(ip, HTTPTRUE, SOCKSTRUE, uniquehash)
    else:
        config.main.logger(2, "[SCANNING]: DNSBL scan on " + str(ip))
        newip = ip.split(".")
        newip = newip[::-1]
        newip = '.'.join(newip)
        contrue = 0
        for blacklist in bll:
            newstring = newip + "." + blacklist
            try:
                answers = dns.resolver.query(newstring,'A')
                if answers:
                    update_ban("dnsbl", None, None, None, blacklist, uniquehash)
                    config.confproto.gline_dnsbl(ip, int(time.time()), int(time.time()) + config.DURATION, blacklist)
                    contrue = 0
                    break
            except dns.resolver.NXDOMAIN:
                contrue += 1
                continue

        if contrue == 5:
            http_connect(ip, HTTPTRUE, SOCKSTRUE, uniquehash)

def http_connect_threads(ip, port, uniquehash):
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
                update_ban("http", port, None, "Non-SSL", None, uniquehash)
                config.confproto.gline_http(ip, int(time.time()), int(time.time()) + config.DURATION, port)
                tcp.close()
                break
    except socket.error, v:
        pass

def https_connect_threads(ip, port, uniquehash):
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
                update_ban("http", port, None, "SSL", None, uniquehash)
                config.confproto.gline_http(ip, int(time.time()), int(time.time()) + config.DURATION, port)
                ssl_sock.close()
                break
    except socket.error, v:
        pass

def http_connect(ip, HTTPTRUE, SOCKSTRUE, uniquehash):
    if HTTPTRUE == 0:
        sockscheck(ip, SOCKSTRUE, uniquehash)
    else:
        config.main.logger(2, "[SCANNING]: HTTP Connect on " + str(ip))
        ports = [80,81,1075,3128,4480,6588,7856,8000,8080,8081,8090,7033,8085,8095,8100,8105,8110,1039,1050,1080,1098,11055,1200,19991,3332,3382,35233,443,444,4471,4480,5000,5490,5634,5800,63000,63809,65506,6588,6654,6661,6663,6664,6665,6667,6668,7070,7868,808,8085,8082,8118,8888,9000,9090,9988]

        for newport in ports:
            http = Process(target=http_connect_threads, args=(ip, newport, uniquehash))
            http.start()
            https = Process(target=https_connect_threads, args=(ip, newport, uniquehash))
            https.start()

        sockscheck(ip, SOCKSTRUE, uniquehash)

def isSocks4(host, port, soc):
    ipaddr = socket.inet_aton(host)
    packet4 = "\x04\x01" + pack(">H",port) + ipaddr + "\x00"
    soc.sendall(packet4)
    data = soc.recv(8)
    if(len(data)<2):
        # Null response
        return False
    if data[0] != "\x00":
        # Bad data
        return False
    if data[1] != "\x5A":
        # Server returned an error
        return False
    return True

def isSocks5(host, port, soc):
    soc.sendall("\x05\x01\x00")
    data = soc.recv(2)
    if(len(data)<2):
        # Null response
        return False
    if data[0] != "\x05":
        # Not socks5
        return False
    if data[1] != "\x00":
        # Requires authentication
        return False
    return True

def sockscheck(ip, SOCKSTRUE, uniquehash):
    if SOCKSTRUE != 0:
        ports = [1080,1075,10000,10080,10099,10130,10242,10777,1025,1026,1027,1028,1029,1030,1031,1032,1033,1039,1050,1066,1081,1098,11011,11022,11033,11055,11171,1122,11225,1180,1182,1200,1202,1212,1234,12654,1337,14841,16591,17327,1813,18888,1978,1979,19991,2000,21421,22277,2280,24971,24973,25552,25839,26905,28882,29992,3127,3128,32167,3330,3380,34610,3801,3867,40,4044,41080,41379,43073,43341,443,44548,4471,43371,44765,4914,49699,5353,559,58,6000,62385,63808,6551,6561,6664,6748,6969,7007,7080,8002,8009,8020,8080,8085,8111,8278,8751,8888,9090,9100,9988,9999,59175,5001,19794,36510]

        def getSocksVersion(proxy, port, uniquehash):
            newprox = str(proxy) + ":" + str(port)
            host = proxy
            sch = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sch.settimeout(2)
            try:
                sch.connect((host, port))
                if(isSocks4(host, port, sch)):
                    sch.close()
                    update_ban("socks", port, "4", None, None, uniquehash)
                    config.confproto.gline_socks(ip, int(time.time()), int(time.time()) + config.DURATION, port, "4")
                    return
                elif(isSocks5(host, port, sch)):
                    sch.close()
                    update_ban("socks", port, "5", None, None, uniquehash)
                    config.confproto.gline_socks(ip, int(time.time()), int(time.time()) + config.DURATION, port, "5")
                    return
                else:
                    sch.close()
                    return 0
            except socket.timeout:
                sch.close()
                return 0
            except socket.error:
                sch.close()
                return 0
        config.main.logger(2, "[SCANNING]: SOCKS on " + str(ip))
        for newport in ports:
            socksc = Process(target=getSocksVersion, args=(ip, newport, uniquehash))
            socksc.start()

        return
    return
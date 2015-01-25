import sys
import socket
import string
import signal
import time
import config
from proxy import getTrueIP, DNSBL
from settings import is_settable, get_set, update_settings, get_set_value, get_dnsbl_value, get_http_value, get_socks_value, isExempt, checkexpired
from commands import privmsg_parser
from multiprocessing import Process, Queue

class P10Server(object):
    def signal_handler(self, signal, frame):
        config.s.send("%sAAA Q :Shutdown received from terminal\n" % (config.SERVER_NUMERIC))
        config.main.logger(1, "[WRITE]: %sAAA Q :Shutdown received from terminal" % (config.SERVER_NUMERIC))
        config.s.send("%s SQ %s 0 :Shutdown received from terminal\n" % (config.SERVER_NUMERIC, config.SERVER_HOST_NAME))
        config.main.logger(1, "[WRITE]: %s SQ %s 0 :Shutdown received from terminal" % (config.SERVER_NUMERIC, config.SERVER_HOST_NAME))
        sys.exit()

    def connect(self, time):
        config.s.connect((config.HOST, config.PORT))
        config.s.send("PASS %s\n" % (config.SERVER_PASS))
        config.main.logger(5, "[WRITE]: PASS %s" % (config.SERVER_PASS))
        config.s.send("SERVER %s %s %d %d J10 %s]]] :%s\n" % (config.SERVER_HOST_NAME, config.HOPS, time, time, config.SERVER_NUMERIC, config.SERVER_DESCRIPTION))
        config.main.logger(5, "[WRITE]: SERVER %s %s %d %d J10 %s]]] :%s" % (config.SERVER_HOST_NAME, config.HOPS, time, time, config.SERVER_NUMERIC, config.SERVER_DESCRIPTION))

    def loadclient(self, nclient, time, botname, bothost, botmode, servernumeric, botdescription):
        newclient = chr(ord('A')+nclient)
        config.s.send("%s N %s 1 %d %s %s %s AAAAA%s %sAA%s :%s\n" % (config.SERVER_NUMERIC, botname, time, botname, bothost, botmode, newclient, config.SERVER_NUMERIC, newclient, botdescription))
        config.main.logger(5, "[WRITE]: %s N %s 1 %d %s %s %s AAAAA%s %sAA%s :%s" % (config.SERVER_NUMERIC, botname, time, botname, bothost, botmode, newclient, config.SERVER_NUMERIC, newclient, botdescription))

    def joinchannel(self, time, clientid, channel):
        config.s.send("%s B %s %d %sAA%s:o\n" % (config.SERVER_NUMERIC, channel, time, config.SERVER_NUMERIC, clientid))
        config.main.logger(5, "[WRITE]: %s B %s %d %sAA%s:o" % (config.SERVER_NUMERIC, channel, time, config.SERVER_NUMERIC, clientid))
        config.s.send("%sAAA M %s +o %sAA%s %d\n" % (config.SERVER_NUMERIC, channel, config.SERVER_NUMERIC, clientid, time)) # Unless our server is U-Lined, this won't work #
        config.main.logger(5, "[WRITE]: %sAAA M %s +o %sAA%s %d" % (config.SERVER_NUMERIC, channel, config.SERVER_NUMERIC, clientid, time))

    def eob(self):
        config.s.send("%s EB\n" % (config.SERVER_NUMERIC))
        config.main.logger(5, "[WRITE]: %s EB" % (config.SERVER_NUMERIC))

    def notice(self, target, message):
        config.s.send("%sAAA O %s :%s\n" % (config.SERVER_NUMERIC, target, message))

    def privmsg(self, target, message):
        config.s.send("%sAAA P %s :%s\n" % (config.SERVER_NUMERIC, target, message))

    def gline_http(self, ip, timewo, timew, port):
        newmessage = config.HTTP_BAN_MSG.replace("{network}", str(config.NETWORK_NAME)).replace("{port}", str(port))
        config.s.send("%s GL * +*@%s %d %d %d :%s\n" % (config.SERVER_NUMERIC, ip, config.DURATION, timewo, timew, newmessage))
        config.main.logger(2, "[WRITE][HTTP_CONNECT]: %s GL * +*@%s %d %d %d :%s" % (config.SERVER_NUMERIC, ip, config.DURATION, timewo, timew, newmessage))

    def gline_dnsbl(self, ip, timewo, timew, blacklist):
        newmessage = config.DNSBL_BAN_MSG.replace("{network}", str(config.NETWORK_NAME)).replace("{list}", str(blacklist))
        config.s.send("%s GL * +*@%s %d %d %d :%s\n" % (config.SERVER_NUMERIC, ip, config.DURATION, timewo, timew, newmessage))
        config.main.logger(2, "[WRITE][DNSBL_FOUND]: %s GL * +*@%s %d %d %d :%s" % (config.SERVER_NUMERIC, ip, config.DURATION, timewo, timew, newmessage))

    def gline_socks(self, ip, timewo, timew, port, version):
        newmessage = config.SOCKS_BAN_MSG.replace("{network}", str(config.NETWORK_NAME)).replace("{port}", str(port)).replace("{version}", str(version))
        config.s.send("%s GL * +*@%s %d %d %d :%s\n" % (config.SERVER_NUMERIC, ip, config.DURATION, timewo, timew, newmessage))
        config.main.logger(2, "[WRITE][SOCKS%s_FOUND]: %s GL * +*@%s %d %d %d :%s" % (version, config.SERVER_NUMERIC, ip, config.DURATION, timewo, timew, newmessage))

    def startbuffer(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        readbuffer = ""
        uplinkid = ""
        uplinkname = ""
        userlist = []
        complete = 0
        while 1:
            readbuffer=readbuffer + config.s.recv(32768)
            temp=string.split(readbuffer, "\n")
            readbuffer=temp.pop()
            for line in temp:
                config.main.logger(4, "[READ]: " + line)
                line=string.rstrip(line)
                line=string.split(line)
                # Get initial data from uplink #
                if(line[0] == "SERVER"):
                    if uplinkid == line[6][:2]:
                        config.main.logger(1, "[ERROR][FATAL]: Uplink ID matches POPM ID. Exiting")
                        sys.exit(0)
                    else:
                        uplinkid = line[6][:2]
                        uplinkname = line[1]

                # Create our user dictionary #
                if(line[1] == "N"):
                    try:
                        if(":" in line[8]):
                            userlist.append("%s:%s" % (line[8].split(":")[0], line[11]))
                            config.main.logger(3, "[INFO]: New userlist is " + str(userlist))
                    except IndexError:
                        try:
                            userlist.append("%s:%s" % (line[8].split(":")[0], line[10]))
                            config.main.logger(3, "[INFO]: New userlist is " + str(userlist))
                        except IndexError:
                            pass
                    except IndexError:
                        pass

                # Add users as they authenticate #
                if(line[1] == "AC"):
                    userlist.append("%s:%s" % (line[3], line[2]))
                    config.main.logger(3, "[INFO]: New userlist is " + str(userlist))

                # Acknowldge the netburst #
                if(line[0] == uplinkid and line[1] == "EB" and complete == 0):
                    config.s.send("%s EA\n" % (config.SERVER_NUMERIC))
                    config.main.logger(5, "[WRITE]: %s EA" % (config.SERVER_NUMERIC))
                    complete = 1

                # Check for ID collisons #
                if(line[1] == "S"):
                    if uplinkid == line[7][:2]:
                        config.main.logger(1, "[ERROR][FATAL]: Server %s has same ID as POPM. Exiting" % (line[2]))
                        sys.exit(0)

                # Keep alive stuff #
                if(line[0] == uplinkid and line[1] == "Z"):
                    config.s.send("%s G :%s\n" % (config.SERVER_NUMERIC, config.SERVER_HOST_NAME))
                    config.main.logger(6, "[WRITE]: %s G :%s" % (config.SERVER_NUMERIC, config.SERVER_HOST_NAME))
                if(line[0] == uplinkid and line[1] == "G"):
                    config.s.send("%s Z %s %s 0 %s\n" % (config.SERVER_NUMERIC, config.SERVER_HOST_NAME, line[2][1:], line[4]))
                    config.main.logger(6, "[WRITE]: %s Z %s %s 0 %s" % (config.SERVER_NUMERIC, config.SERVER_HOST_NAME, line[2][1:], line[4]))

                # If we were squit, then abandon ship #
                if(line[1] == "SQ" and line[2] == uplinkname):
                    config.main.logger(1, "[ERROR][FATAL]: Received SQUIT from uplink. Exiting")
                    sys.exit(0)

                # Get incomming connections #
                if(line[1] == "N"):
                    try:
                        if config.SCAN_ON_BURST == 1:
                            trueIP = str(getTrueIP(line[6]))
                            checkexpired()
                            if not isExempt(trueIP):
                                newip = Process(target=DNSBL, args=(trueIP, line[2], get_dnsbl_value(), get_http_value(), get_socks_value()))
                                newip.start()
                        else:
                            if complete == 1:
                                trueIP = str(getTrueIP(line[6]))
                                checkexpired()
                                if not isExempt(trueIP):
                                    newip = Process(target=DNSBL, args=(trueIP, line[2], get_dnsbl_value(), get_http_value(), get_socks_value()))
                                    newip.start()
                    except IndexError:
                        pass

                # Commands (efficienize me) #
                if(line[1] == "P" and line[2][:1] == "#" or line[1] == "P" and line[2] == "%sAAA" % (config.SERVER_NUMERIC)):
                    privmsg_parser(userlist, line)
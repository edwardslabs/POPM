import sys
import socket
import socks
import string
import signal
import time
import config
from proxy import DNSBL, getTrueIP
from settings import is_settable, get_set, update_settings, get_set_value, get_dnsbl_value, get_http_value, get_socks_value, isExempt, checkexpired
from commands import privmsg
from multiprocessing import Process, Queue

class Server:

    def signal_handler(signal, frame):
        config.s.send("%sAAA Q :Shutdown received from terminal\n" % (config.SERVER_NUMERIC))
        print("[WRITE]: %sAAA Q :Shutdown received from terminal" % (config.SERVER_NUMERIC))
        config.s.send("%s SQ %s 0 :Shutdown received from terminal\n" % (config.SERVER_NUMERIC, config.SERVER_HOST_NAME))
        print("[WRITE]: %s SQ %s 0 :Shutdown received from terminal" % (config.SERVER_NUMERIC, config.SERVER_HOST_NAME))
        sys.exit()

    if __name__ == "__main__":
        signal.signal(signal.SIGINT, signal_handler)
        config.s.connect((config.HOST, config.PORT))
        boot_time = int(time.time())
        config.s.send("PASS %s\n" % (config.SERVER_PASS))
        print("[WRITE]: PASS %s" % (config.SERVER_PASS))
        config.s.send("SERVER %s %s %d %d J10 %s]]] :%s\n" % (config.SERVER_HOST_NAME, config.HOPS, boot_time, boot_time, config.SERVER_NUMERIC, config.SERVER_DESCRIPTION))
        print("[WRITE]: SERVER %s %s %d %d J10 %s]]] :%s" % (config.SERVER_HOST_NAME, config.HOPS, boot_time, boot_time, config.SERVER_NUMERIC, config.SERVER_DESCRIPTION))
        config.s.send("%s N %s 1 %d %s %s %s AAAAAA %sAAA :%s\n" % (config.SERVER_NUMERIC, config.BOT_NAME, boot_time, config.BOT_NAME, config.BOT_HOST, config.BOT_MODE, config.SERVER_NUMERIC, config.BOT_DESC))
        print("[WRITE]: %s N %s 1 %d %s %s %s AAAAAA %sAAA :%s" % (config.SERVER_NUMERIC, config.BOT_NAME, boot_time, config.SERVER_NUMERIC, config.BOT_HOST, config.BOT_MODE, config.BOT_NAME, config.BOT_DESC))
        config.s.send("%s B %s %d %sAAA:o\n" % (config.SERVER_NUMERIC, config.DEBUG_CHANNEL, boot_time, config.SERVER_NUMERIC))
        print("[WRITE]: %s B %s %d %sAAA:o" % (config.SERVER_NUMERIC, config.DEBUG_CHANNEL, boot_time, config.SERVER_NUMERIC))
        config.s.send("%sAAA M %s +o %sAAA %d\n" % (config.SERVER_NUMERIC, config.DEBUG_CHANNEL, config.SERVER_NUMERIC, boot_time)) # Unless our server is U-Lined, this won't work #
        print("[WRITE]: %sAAA M %s +o %sAAA %d" % (config.SERVER_NUMERIC, config.DEBUG_CHANNEL, config.SERVER_NUMERIC, boot_time))
        config.s.send("%s EB\n" % (config.SERVER_NUMERIC))
        print("[WRITE]: %s EB" % (config.SERVER_NUMERIC))
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
                    try:
                        if(":" in line[8]):
                            try:
                                if line[12]:
                                    userlist.append("%s:%s" % (line[8].split(":")[0], line[11]))
                            except IndexError:
                                    userlist.append("%s:%s" % (line[8].split(":")[0], line[10]))
                            print "[INFO]: New userlist is " + str(userlist)
                    except IndexError:
                            pass

                # Add users as they authenticate #
                if(line[1] == "AC"):
                    userlist.append("%s:%s" % (line[3], line[2]))
                    print "[INFO]: New userlist is " + str(userlist)

                # Acknowldge the netburst #
                if(line[0] == uplinkid and line[1] == "EB" and complete == 0):
                    config.s.send("%s EA\n" % (config.SERVER_NUMERIC))
                    print("[WRITE]: %s EA" % (config.SERVER_NUMERIC))
                    complete = 1

                # Check for ID collisons #
                if(line[1] == "S"):
                    if uplinkid == line[7][:2]:
                        print("[ERROR][FATAL]: Server %s has same ID as POPM. Exiting\n" % (line[2]))
                        sys.exit(0)

                # Keep alive stuff #
                if(line[0] == uplinkid and line[1] == "Z"):
                    config.s.send("%s G :%s\n" % (config.SERVER_NUMERIC, config.SERVER_HOST_NAME))
                    print("[WRITE]: %s G :%s" % (config.SERVER_NUMERIC, config.SERVER_HOST_NAME))
                if(line[0] == uplinkid and line[1] == "G"):
                    config.s.send("%s Z %s %s 0 %s\n" % (config.SERVER_NUMERIC, config.SERVER_HOST_NAME, line[2][1:], line[4]))
                    print("[WRITE]: %s Z %s %s 0 %s" % (config.SERVER_NUMERIC, config.SERVER_HOST_NAME, line[2][1:], line[4]))

                # If we were squit, then abandon ship #
                if(line[1] == "SQ" and line[2] == uplinkname):
                    print"[ERROR][FATAL]: Received SQUIT from uplink. Exiting\n"
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
                    privmsg(userlist, line)
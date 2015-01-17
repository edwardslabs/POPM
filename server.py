import socket
import time
import string
import signal
import sys
from threading import Thread
from thread import start_new_thread, allocate_lock
from config import *
from proxy import DNSBL
from access import show_access, get_level_req, update_access, get_acc, access_level
from settings import is_settable, get_set, update_settings, get_set_value
from signals import signal_handler
from commands import privmsg
from multiprocessing import Process, Queue
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
            newip = Process(target=DNSBL, args=(line[6], line[2]))
            newip.start()

        # Commands (efficienize me) #
        if(line[1] == "P" and line[2][:1] == "#" or line[1] == "P" and line[2] == "%sAAA" % (SERVER_NUMERIC)):
            privmsg(userlist, line)
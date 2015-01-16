import socket
import time
import string
import signal
import sys
from dnsbl import *
from config import *
from access import *
from settings import *
from signals import *
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
            thread = Thread(target=dnsbl.DNSBL(line[6], line[2]))
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
                if access_level(target, userlist) > 750:
                    try:
                        s.send("%sAAA O %s :There are %s threads running\n" % (SERVER_NUMERIC, target, threading.activeCount()))
                        print("[WRITE]: %sAAA O %s :There are %s threads running" % (SERVER_NUMERIC, target, threading.activeCount()))
                    except NameError:
                        s.send("%sAAA O %s :There are no threads running\n" % (SERVER_NUMERIC, target))
                        print("[WRITE]: %sAAA O %s :There are no threads running" % (SERVER_NUMERIC, target))
                elif access_level(target, userlist) <= 749:
                    s.send("%sAAA O %s :You lack access to this command\n" % (SERVER_NUMERIC, target))
                    print("[WRITE]: %sAAA O %s :You lack access to this command" % (SERVER_NUMERIC, target))
            elif(line[3].lower() == ":.help" and channel is True or channel is False and line[3].lower() == ":help"):
                if access_level(target, userlist) > 0:
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
                                s.send("%sAAA O %s :and SQUIT reason. Note: When you use DIE, your NickServ account\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :name will be attached to the SQUIT message.\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-\n" % (SERVER_NUMERIC, target))
                            elif line[4].lower() == "set":
                                s.send("%sAAA O %s :-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :SET on its own will display the current configuration\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :for %s. Note, that the SET command can only be used by\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :users with SET access. SET can also take arguments.\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :Below is a list of items you can set in %s\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :To change any of the settings, just type\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :/msg %s SET paramter value\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :Examples:\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :/msg %s SET DNSBL off\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :/msg %s SET HTTP on\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :/msg %s SET SOCKS on\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :/msg %s SET SETTERS 900\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :/msg %s SET DIE 1000\n" % (SERVER_NUMERIC, target, BOT_NAME))
                                s.send("%sAAA O %s :\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :ON/OFF Set Options:\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :http\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :socks\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :dnsbl\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :Access Level Set Options:\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :die\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :setters\n" % (SERVER_NUMERIC, target))
                                s.send("%sAAA O %s :-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-\n" % (SERVER_NUMERIC, target))
                            else:
                                s.send("%sAAA O %s :%s is an unknown command to me.\n" % (SERVER_NUMERIC, target, line[4]))
                    except IndexError:
                        if access_level(target, userlist) > 0:
                            print "IN HELP"
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
                        if access_level(target, userlist) == 1000:
                            if access <= 1000:
                                update_access(line[4], access, target, userlist)
                            else:
                                s.send("%sAAA O %s :Access must be greater than 1000\n" % (SERVER_NUMERIC, target))
                        else:
                            s.send("%sAAA O %s :Access modification can only be done via root (1000 access) users.\n" % (SERVER_NUMERIC, target))
                except IndexError:
                    try:
                        if line[4] != False:
                            if access_level(target, userlist) > 0:
                                show_access(line[4], target)
                    except IndexError:
                        if access_level(target, userlist) > 0:
                            s.send("%sAAA O %s :Account %s has access %s.\n" % (SERVER_NUMERIC, target, get_acc(target, userlist), access_level(target, userlist)))
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
                        account = get_acc(target, userlist)
                        if access_level(target, userlist) >= 900:
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
                        if access_level(target, userlist) >= get_level_req("access_set"):
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
                    if access_level(target, userlist) >= get_level_req("setters"):
                        get_set(target)
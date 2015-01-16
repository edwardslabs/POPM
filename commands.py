import socket
import time
import string
import signal
import sys
from dnsbl import *
from config import *
from access import show_access, get_level_req, update_access, get_acc, access_level
from settings import is_settable, get_set, update_settings, get_set_value
from signals import signal_handler
from server import *

def privmsg(userlist, line):
    channel = False
    target = line[0]
    command = line[3][1:].lower()
    if line[2][:1] == "#":
        channel = True
        channel_target = line[2]
        target = line[0]
    if(command == ".threads" and channel) or (not channel and command == "threads"):
        get_threads(target, userlist, line)
    elif(command == ".help" and channel) or (not channel and command == "help"):
        get_help(target, userlist, line)
    elif(command == ".access" and channel) or (not channel and command == "access"):
        get_access(target, userlist, line)
    elif(command == ".die" and channel) or (not channel and command == "die"):
        die(target, userlist, line)
    elif(command == ".set" and channel) or (not channel and command == "set"):
        do_set(target, userlist, line)
    else:
        command_unknown(target, userlist, line)

def get_threads(target, userlist, line):
    from server import *
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

def get_access(target, userlist, line):
    from server import *
    try:
        if line[5] != False:
            try:
                access = line[5]
                access = int(access)
            except ValueError:
                s.send("%sAAA O %s :Access level must be an integer.\n" % (SERVER_NUMERIC, target))
                return
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

def die(target, userlist, line):
    import sys
    from server import *
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

def do_set(target, userlist, line):
    from server import *
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

def command_unknown(target, userlist, line):
    from server import *
    if access_level(target, userlist) > 0:
        arlen = len(line)
        newstring = ""
        i = 3
        while i < arlen:
            if newstring == "":
                newstring = line[i]
            else:
                newstring = newstring + " " + line[i]
            i += 1
        s.send("%sAAA O %s :Unknown command %s\n" % (SERVER_NUMERIC, target, newstring[1:]))

def get_help(target, userlist, line):
    from server import *
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
                s.send("%sAAA O %s :-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-\n" % (SERVER_NUMERIC, target, BOT_NAME))
                s.send("%sAAA O %s :%s gives authorized users extra control over the proxy monitoring system.\n" % (SERVER_NUMERIC, target, BOT_NAME))
                s.send("%sAAA O %s :General commands:\n" % (SERVER_NUMERIC, target))
                s.send("%sAAA O %s :Threads:        Shows current number of threads\n" % (SERVER_NUMERIC, target))
                s.send("%sAAA O %s :Access:         Shows access for accounts\n" % (SERVER_NUMERIC, target))
                s.send("%sAAA O %s :Set:            Sets the configuration for POPM\n" % (SERVER_NUMERIC, target))
                s.send("%sAAA O %s :Die:            Terminates POPM and disconnects from %s\n" % (SERVER_NUMERIC, target, NETWORK_NAME))
                s.send("%sAAA O %s :-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-\n" % (SERVER_NUMERIC, target))
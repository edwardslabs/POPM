import socket
import time
import string
import signal
import sys
from config import *
from access import show_access, get_level_req, update_access, get_acc, access_level
from settings import is_settable, get_set, update_settings, get_set_value, get_die, get_say
from server import *

def privmsg(userlist, line):
    channel = False
    target = line[0]
    command = line[3][1:].lower()
    if line[2][:1] == "#":
        channel = True
        channel_target = line[2]
        target = line[0]
    if command[:1] == PREFIX and channel:
        command = command[1:]

    # Commands list #
    if(command == "threads"):
        get_threads(target, userlist, line)

    elif(command == "help"):
        get_help(target, userlist, line)

    elif(command == "access"):
        get_access(target, userlist, line)

    elif(command == "die"):
        die(target, userlist, line)

    elif(command == "set"):
        do_set(target, userlist, line)

    elif (command == "say"):
        say(target, channel, userlist, line)

    elif (command == "emote"):
        emote(target, channel, userlist, line)

    elif(not channel):
        command_unknown(target, userlist, line)

def gline_http(ip, timewo, timew, port):
    from server import *
    from config import *
    s.send("%s GL * +*@%s %d %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]\n" % (SERVER_NUMERIC, ip, DURATION, timewo, timew, NETWORK_NAME, port))
    print("[WRITE][HTTP_CONNECT]: %s GL * +*@%s %d %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]" % (SERVER_NUMERIC, ip, DURATION, timewo, timew, NETWORK_NAME, port))

def gline_dnsbl(ip, timewo, timew, blacklist):
    from server import *
    from config import *
    s.send("%s GL * +*@%s %d %d %d :AUTO Your IP is listed as being an infected drone, or otherwise not fit to join %s. [Detected %s]\n" % (SERVER_NUMERIC, ip, DURATION, timewo, timew, NETWORK_NAME, blacklist))
    print("[WRITE][DNSBL_FOUND]: %s GL * +*@%s %d %d %d :AUTO Your IP is listed as being an infected drone, or otherwise not fit to join %s. [Detected %s]" % (SERVER_NUMERIC, ip, DURATION, timewo, timew, NETWORK_NAME, blacklist))

def get_threads(target, userlist, line):
    from server import *
    if access_level(target, userlist) > 750:
        try:
            serv_notice(target, "There are %s threads running" % (multiprocessing.cpu_count()))
            print("[WRITE]: %sAAA O %s :There are %s threads running" % (SERVER_NUMERIC, target, multiprocessing.cpu_count()))
        except NameError:
            serv_notice(target, "There are no threads running")
            print("[WRITE]: %sAAA O %s :There are no threads running" % (SERVER_NUMERIC, target))
    elif access_level(target, userlist) <= 749:
        serv_notice(target, "You lack access to this command.")
        print("[WRITE]: %sAAA O %s :You lack access to this command" % (SERVER_NUMERIC, target))

def get_access(target, userlist, line):
    try:
        if line[5] != False:
            try:
                access = line[5]
                access = int(access)
            except ValueError:
                serv_notice(target, "Access level must be an integer.")
                return
            if access_level(target, userlist) == 1000:
                if access <= 1000:
                    update_access(line[4], access, target, userlist)
                else:
                    serv_notice(target, "Access must be greater than 1000.")
            else:
                serv_notice(target, "Access modification can only be done via root (1000 access) users.")
    except IndexError:
        try:
            if line[4] != False:
                if access_level(target, userlist) > 0:
                    show_access(line[4], target)
        except IndexError:
            if access_level(target, userlist) > 0:
                serv_notice(target, "Account %s has access %s." % (get_acc(target, userlist), access_level(target, userlist)))

def say(target, channel, userlist, line):
    if access_level(target, userlist) >= get_say():
        try:
            if line[4] != False:
                try:
                    if line[5] != False:
                        arlen = len(line)
                        newstring = ""
                        if channel and line[4][:1] != "#":
                            taruser = line[2]
                            i = 4
                        else:
                            taruser = line[4]
                            i = 5
                        while i < arlen:
                            if newstring == "":
                                newstring = line[i]
                            else:
                                newstring = newstring + " " + line[i]
                            i += 1
                        serv_privmsg(taruser, "%s" % (newstring))
                        print("[WRITE]: %sAAA P %s :%s" % (SERVER_NUMERIC, taruser, newstring))
                except IndexError:
                    arlen = len(line)
                    newstring = ""
                    if channel and line[4][:1] != "#":
                        taruser = line[2]
                        i = 4
                    else:
                        serv_notice(target, "Insufficient paramaters for SAY")
                        print("[WRITE]: %sAAA O %s :Insufficient paramaters for SAY" % (SERVER_NUMERIC, target))
                        return
                    while i < arlen:
                        if newstring == "":
                            newstring = line[i]
                        else:
                            newstring = newstring + " " + line[i]
                        i += 1
                    serv_privmsg(taruser, "%s" % (newstring))
                    print("[WRITE]: %sAAA P %s :%s" % (SERVER_NUMERIC, taruser, newstring))
        except IndexError:
                    serv_notice(target, "Insufficient paramaters for SAY")
                    print("[WRITE]: %sAAA O %s :Insufficient paramaters for SAY" % (SERVER_NUMERIC, target))
    else:
        serv_notice(target, "You lack access to this command.")

def emote(target, channel, userlist, line):
    if access_level(target, userlist) >= get_say():
        try:
            if line[4] != False:
                try:
                    if line[5] != False:
                        arlen = len(line)
                        newstring = ""
                        if channel and line[4][:1] != "#":
                            taruser = line[2]
                            i = 4
                        else:
                            taruser = line[4]
                            i = 5
                        while i < arlen:
                            if newstring == "":
                                newstring = line[i]
                            else:
                                newstring = newstring + " " + line[i]
                            i += 1
                        serv_privmsg(taruser, "\001ACTION %s\001" % (newstring))
                        print("[WRITE]: %sAAA P %s :\001ACTION %s\001" % (SERVER_NUMERIC, taruser, newstring))
                except IndexError:
                    arlen = len(line)
                    newstring = ""
                    if channel and line[4][:1] != "#":
                        taruser = line[2]
                        i = 4
                    else:
                        serv_notice(target, "Insufficient paramaters for EMOTE")
                        print("[WRITE]: %sAAA O %s :Insufficient paramaters for EMOTE" % (SERVER_NUMERIC, target))
                        return
                    while i < arlen:
                        if newstring == "":
                            newstring = line[i]
                        else:
                            newstring = newstring + " " + line[i]
                        i += 1
                    serv_privmsg(taruser, "\001ACTION %s\001" % (newstring))
                    print("[WRITE]: %sAAA P %s :\001ACTION %s\001" % (SERVER_NUMERIC, taruser, newstring))
        except IndexError:
                    serv_notice(target, "Insufficient paramaters for EMOTE.")
                    print("[WRITE]: %sAAA O %s :Insufficient paramaters for EMOTE" % (SERVER_NUMERIC, target))
    else:
        serv_notice(target, "You lack access to this command.")

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
            if access_level(target, userlist) >= get_die():
                s.send("%sAAA Q :%s\n" % (SERVER_NUMERIC, newstring))
                print("[WRITE]: %sAAA Q :%s" % (SERVER_NUMERIC, newstring))
                s.send("%s SQ %s 0 :[%s (by %s)]\n" % (SERVER_NUMERIC, SERVER_HOST_NAME, newstring, account))
                print("[WRITE]: %s SQ %s 0 :[%s (by %s)]" % (SERVER_NUMERIC, SERVER_HOST_NAME, newstring, account))
                sys.exit(0)
            else:
                serv_notice(target, "You lack access to this command")
                print("[WRITE]: %sAAA O %s :You lack access to this command" % (SERVER_NUMERIC, target))
    except IndexError:
        serv_notice(target, "Insufficient paramaters for DIE")
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
                                serv_notice(target, "Paramater must be an integer.")
                            if newlevel <= 1000 and newlevel >= 0:
                                update_settings(line[4], newlevel, target)
                            else:
                                serv_notice(target, "Paramater must be an integer between 0 and 1000.")
                    except IndexError:
                        get_set_value(line[4], target)
                else:
                    serv_notice(target, "Invalid SET option.")
            else:
                serv_notice(target, "You lack access to this command.")
    except IndexError:
        if access_level(target, userlist) >= get_level_req("setters"):
            get_set(target)
        else:
            serv_notice(target, "You lack access to this command.")

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
        serv_notice(target, "Unknown command %s." % (newstring[1:]))

def serv_notice(target, message):
    from server import *
    s.send("%sAAA O %s :%s\n" % (SERVER_NUMERIC, target, message))

def serv_privmsg(target, message):
    from server import *
    s.send("%sAAA P %s :%s\n" % (SERVER_NUMERIC, target, message))

def get_help(target, userlist, line):
    from server import *
    if access_level(target, userlist) > 0:
        try:
            if line[4] != False:
                if line[4].lower() == "threads":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (BOT_NAME))
                    serv_notice(target, "THREADS displays the current number of worker threads by %s." % (BOT_NAME))
                    serv_notice(target, "These threads are spawned when an incoming connection is recieved")
                    serv_notice(target, "to check for proxys on the remote host.")
                    serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "access":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (BOT_NAME))
                    serv_notice(target, "ACCESS is a multi-functional command. Access has the ability to")
                    serv_notice(target, "check your access with %s, check other's access, add other users to %s" % (BOT_NAME, BOT_NAME))
                    serv_notice(target, "and to remove users access to %s. At this time, only root users may" % (BOT_NAME))
                    serv_notice(target, "add or remove other users from %s." % (BOT_NAME))
                    serv_notice(target, "Note: To remove a users access, set their access to -1")
                    serv_notice(target, "Examples:")
                    serv_notice(target, "/msg %s ACCESS foobar" % (BOT_NAME))
                    serv_notice(target, "/msg %s ACCESS *" % (BOT_NAME))
                    serv_notice(target, "/msg %s ACCESS foo 950" % (BOT_NAME))
                    serv_notice(target, "/msg %s ACCESS bar -1" % (BOT_NAME))
                    serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "die":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (BOT_NAME))
                    serv_notice(target, "DIE causes %s to quit and POPM to disconnect from %s." % (BOT_NAME, NETWORK_NAME))
                    serv_notice(target, "This will completly stop the program and will have to")
                    serv_notice(target, "be restarted locally. DIE takes arguments for the QUIT message")
                    serv_notice(target, "and SQUIT reason. Note: When you use DIE, your NickServ account")
                    serv_notice(target, "name will be attached to the SQUIT message.")
                    serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "say":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (BOT_NAME))
                    serv_notice(target, "/msg %s SAY <#channel|nick> <text>" % (BOT_NAME))
                    serv_notice(target, "Makes %s send a message to a specified nick/channel." % (BOT_NAME))
                    serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "emote":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (BOT_NAME))
                    serv_notice(target, "/msg %s EMOTE <#channel|nick> <text>" % (BOT_NAME))
                    serv_notice(target, "Makes %s do the equivelent of /me to the specified nick/channel." % (BOT_NAME))
                    serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "set":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (BOT_NAME))
                    serv_notice(target, "SET on its own will display the current configuration")
                    serv_notice(target, "for %s. Note, that the SET command can only be used by" % (BOT_NAME))
                    serv_notice(target, "users with SET access. SET can also take arguments.")
                    serv_notice(target, "Below is a list of items you can set in %s" % (BOT_NAME))
                    serv_notice(target, "To change any of the settings, just type")
                    serv_notice(target, "/msg %s SET paramter value" % (BOT_NAME))
                    serv_notice(target, "")
                    serv_notice(target, "Examples:")
                    serv_notice(target, "/msg %s SET DNSBL off" % (BOT_NAME))
                    serv_notice(target, "/msg %s SET HTTP on" % (BOT_NAME))
                    serv_notice(target, "/msg %s SET SOCKS on" % (BOT_NAME))
                    serv_notice(target, "/msg %s SET SETTERS 900" % (BOT_NAME))
                    serv_notice(target, "/msg %s SET DIE 1000" % (BOT_NAME))
                    serv_notice(target, "")
                    serv_notice(target, "ON/OFF Set Options:")
                    serv_notice(target, "http")
                    serv_notice(target, "socks")
                    serv_notice(target, "dnsbl")
                    serv_notice(target, "Access Level Set Options:")
                    serv_notice(target, "die")
                    serv_notice(target, "setters")
                    serv_notice(target, "say")
                    serv_notice(target, "emote")
                    serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                else:
                    serv_notice(target, "%s is an unknown command to me." % (line[4]))
        except IndexError:
            if access_level(target, userlist) > 0:
                serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (BOT_NAME))
                serv_notice(target, "%s gives authorized users extra control over the proxy monitoring system." % (BOT_NAME))
                serv_notice(target, "General commands:")
                serv_notice(target, "Threads:        Shows current number of threads")
                serv_notice(target, "Access:         Shows access for accounts")
                serv_notice(target, "Set:            Sets the configuration for POPM")
                serv_notice(target, "Say:            Makes %s talk" % (BOT_NAME))
                serv_notice(target, "Emote:          Makes %s do the equivelent of /me" % (BOT_NAME))
                serv_notice(target, "Die:            Terminates POPM and disconnects from %s" % (NETWORK_NAME))
                serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
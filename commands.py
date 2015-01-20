import time
import string
import sys
import config
from access import show_access, get_level_req, update_access, get_acc, access_level
from settings import is_settable, get_set, update_settings, get_set_value, get_die, get_say
global config
global sys

def privmsg(userlist, line):
    channel = False
    target = line[0]
    command = line[3][1:].lower()
    if line[2][:1] == "#":
        channel = True
        channel_target = line[2]
        target = line[0]
    if command[:1] == config.PREFIX and channel:
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
    config.s.send("%s GL * +*@%s %d %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]\n" % (config.SERVER_NUMERIC, ip, config.DURATION, timewo, timew, config.NETWORK_NAME, port))
    print("[WRITE][HTTP_CONNECT]: %s GL * +*@%s %d %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]" % (config.SERVER_NUMERIC, ip, config.DURATION, timewo, timew, config.NETWORK_NAME, port))

def gline_dnsbl(ip, timewo, timew, blacklist):
    config.s.send("%s GL * +*@%s %d %d %d :AUTO Your IP is listed as being an infected drone, or otherwise not fit to join %s. [Detected %s]\n" % (config.SERVER_NUMERIC, ip, config.DURATION, timewo, timew, config.NETWORK_NAME, blacklist))
    print("[WRITE][DNSBL_FOUND]: %s GL * +*@%s %d %d %d :AUTO Your IP is listed as being an infected drone, or otherwise not fit to join %s. [Detected %s]" % (config.SERVER_NUMERIC, ip, config.DURATION, timewo, timew, config.NETWORK_NAME, blacklist))

def get_threads(target, userlist, line):
    if access_level(target, userlist) > 750:
        try:
            serv_notice(target, "There are %s threads running" % (multiprocessing.cpu_count()))
        except NameError:
            serv_notice(target, "There are no threads running")
    elif access_level(target, userlist) <= 749:
        serv_notice(target, "You lack access to this command.")

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
                except IndexError:
                    arlen = len(line)
                    newstring = ""
                    if channel and line[4][:1] != "#":
                        taruser = line[2]
                        i = 4
                    else:
                        serv_notice(target, "Insufficient paramaters for SAY")
                        return
                    while i < arlen:
                        if newstring == "":
                            newstring = line[i]
                        else:
                            newstring = newstring + " " + line[i]
                        i += 1
                    serv_privmsg(taruser, "%s" % (newstring))
        except IndexError:
                    serv_notice(target, "Insufficient paramaters for SAY")
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
                except IndexError:
                    arlen = len(line)
                    newstring = ""
                    if channel and line[4][:1] != "#":
                        taruser = line[2]
                        i = 4
                    else:
                        serv_notice(target, "Insufficient paramaters for EMOTE")
                        return
                    while i < arlen:
                        if newstring == "":
                            newstring = line[i]
                        else:
                            newstring = newstring + " " + line[i]
                        i += 1
                    serv_privmsg(taruser, "\001ACTION %s\001" % (newstring))
        except IndexError:
                    serv_notice(target, "Insufficient paramaters for EMOTE.")
    else:
        serv_notice(target, "You lack access to this command.")

def die(target, userlist, line):
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
                config.s.send("%sAAA Q :%s\n" % (config.SERVER_NUMERIC, newstring))
                config.s.send("%s SQ %s 0 :[%s (by %s)]\n" % (config.SERVER_NUMERIC, config.SERVER_HOST_NAME, newstring, account))
                print("[WRITE]: %s SQ %s 0 :[%s (by %s)]" % (config.SERVER_NUMERIC, config.SERVER_HOST_NAME, newstring, account))
                sys.exit(0)
            else:
                serv_notice(target, "You lack access to this command")
    except IndexError:
        serv_notice(target, "Insufficient paramaters for DIE")

def do_set(target, userlist, line):
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
    config.s.send("%sAAA O %s :%s\n" % (config.SERVER_NUMERIC, target, message))

def serv_privmsg(target, message):
    config.s.send("%sAAA P %s :%s\n" % (config.SERVER_NUMERIC, target, message))

def get_help(target, userlist, line):
    if access_level(target, userlist) > 0:
        try:
            if line[4] != False:
                if line[4].lower() == "threads":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    serv_notice(target, "THREADS displays the current number of worker threads by %s." % (config.BOT_NAME))
                    serv_notice(target, "These threads are spawned when an incoming connection is recieved")
                    serv_notice(target, "to check for proxys on the remote host.")
                    serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "access":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    serv_notice(target, "ACCESS is a multi-functional command. Access has the ability to")
                    serv_notice(target, "check your access with %s, check other's access, add other users to %s" % (config.BOT_NAME, config.BOT_NAME))
                    serv_notice(target, "and to remove users access to %s. At this time, only root users may" % (config.BOT_NAME))
                    serv_notice(target, "add or remove other users from %s." % (config.BOT_NAME))
                    serv_notice(target, "Note: To remove a users access, set their access to -1")
                    serv_notice(target, "Examples:")
                    serv_notice(target, "/msg %s ACCESS foobar" % (config.BOT_NAME))
                    serv_notice(target, "/msg %s ACCESS *" % (config.BOT_NAME))
                    serv_notice(target, "/msg %s ACCESS foo 950" % (config.BOT_NAME))
                    serv_notice(target, "/msg %s ACCESS bar -1" % (config.BOT_NAME))
                    serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "die":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    serv_notice(target, "DIE causes %s to quit and POPM to disconnect from %s." % (config.BOT_NAME, config.NETWORK_NAME))
                    serv_notice(target, "This will completly stop the program and will have to")
                    serv_notice(target, "be restarted locally. DIE takes arguments for the QUIT message")
                    serv_notice(target, "and SQUIT reason. Note: When you use DIE, your NickServ account")
                    serv_notice(target, "name will be attached to the SQUIT message.")
                    serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "say":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    serv_notice(target, "/msg %s SAY <#channel|nick> <text>" % (config.BOT_NAME))
                    serv_notice(target, "Makes %s send a message to a specified nick/channel." % (config.BOT_NAME))
                    serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "emote":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    serv_notice(target, "/msg %s EMOTE <#channel|nick> <text>" % (config.BOT_NAME))
                    serv_notice(target, "Makes %s do the equivelent of /me to the specified nick/channel." % (config.BOT_NAME))
                    serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "set":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    serv_notice(target, "SET on its own will display the current configuration")
                    serv_notice(target, "for %s. Note, that the SET command can only be used by" % (config.BOT_NAME))
                    serv_notice(target, "users with SET access. SET can also take arguments.")
                    serv_notice(target, "Below is a list of items you can set in %s" % (config.BOT_NAME))
                    serv_notice(target, "To change any of the settings, just type")
                    serv_notice(target, "/msg %s SET paramter value" % (config.BOT_NAME))
                    serv_notice(target, "")
                    serv_notice(target, "Examples:")
                    serv_notice(target, "/msg %s SET DNSBL off" % (config.BOT_NAME))
                    serv_notice(target, "/msg %s SET HTTP on" % (config.BOT_NAME))
                    serv_notice(target, "/msg %s SET SOCKS on" % (config.BOT_NAME))
                    serv_notice(target, "/msg %s SET SETTERS 900" % (config.BOT_NAME))
                    serv_notice(target, "/msg %s SET DIE 1000" % (config.BOT_NAME))
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
                serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                serv_notice(target, "%s gives authorized users extra control over the proxy monitoring system." % (config.BOT_NAME))
                serv_notice(target, "General commands:")
                serv_notice(target, "Threads:        Shows current number of threads")
                serv_notice(target, "Access:         Shows access for accounts")
                serv_notice(target, "Set:            Sets the configuration for POPM")
                serv_notice(target, "Say:            Makes %s talk" % (config.BOT_NAME))
                serv_notice(target, "Emote:          Makes %s do the equivelent of /me" % (config.BOT_NAME))
                serv_notice(target, "Die:            Terminates POPM and disconnects from %s" % (config.NETWORK_NAME))
                serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
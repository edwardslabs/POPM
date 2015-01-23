import time
import string
import sys
import config
from access import show_access, get_level_req, update_access, get_acc, access_level
from settings import is_settable, get_set, update_settings, get_set_value, get_die, get_say, addexempt, delexempt, get_modify_exempt, get_view_exempt, exemption_data
from proxy import isIP, isIPv6
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

    if command[:1] != config.PREFIX and channel:
        return

    if command[:1] == config.PREFIX and channel:
        if access_level(target, userlist) is not False:
            command = command[1:]
        else:
            return

    # Commands list #
    if(command == "threads"):
        get_threads(target, userlist, line)

    elif(command == "help"):
        get_help(target, userlist, line)

    elif(command == "access"):
        get_access(target, userlist, line)

    elif(command == "die"):
        die(target, userlist, line)

    elif(command == "restart"):
        restart(target, userlist, line)

    elif(command == "set"):
        do_set(target, userlist, line)

    elif(command == "say"):
        say(target, channel, userlist, line)

    elif(command == "emote"):
        emote(target, channel, userlist, line)

    elif(command == "exempt"):
        exempt(target, userlist, line)

    elif(not channel):
        command_unknown(target, userlist, line)

def get_threads(target, userlist, line):
    if access_level(target, userlist) > 750:
        try:
            serv_notice(target, "There are %s threads running" % (multiprocessing.cpu_count()))
        except NameError:
            serv_notice(target, "There are no threads running")
    elif access_level(target, userlist) <= 749:
        serv_notice(target, "You lack access to this command.")

def get_access(target, userlist, line):
    from access import my_access
    try:
        if line[5]:
            try:
                access = line[5]
                access = int(access)
            except ValueError:
                serv_notice(target, "Access level must be an integer.")
                return
            if my_access(target, userlist) == 1000:
                if access <= 1000:
                    update_access(line[4], access, target, userlist)
                else:
                    serv_notice(target, "Access must be greater than 1000.")
            else:
                serv_notice(target, "Access modification can only be done via root (1000 access) users.")
    except IndexError:
        try:
            if line[4]:
                if my_access(target, userlist) > 0:
                    show_access(line[4], target)
        except IndexError:
            if my_access(target, userlist) > 0:
                serv_notice(target, "Account %s has access %s." % (get_acc(target, userlist), access_level(target, userlist)))

def exempt(target, userlist, line):
    try:
        if line[4].lower() == "add":
            if access_level(target, userlist) >= get_modify_exempt():
                try:
                    if isIP(line[5]) or isIPv6(line[5]):
                        theip = line[5]
                        try:
                            if line[6][-1] == "s":
                                typetime = 1
                            elif line[6][-1] == "m":
                                typetime = 2
                            elif line[6][-1] == "h":
                                typetime = 3
                            elif line[6][-1] == "d":
                                typetime = 4
                            elif line[6][-1] == "w":
                                typetime = 5
                            elif line[6][-1] == "M":
                                typetime = 6
                            elif line[6][-1] == "y":
                                typetime = 7
                            elif line[6] == "0":
                                typetime = 8
                            else:
                                #print "received %s" % (line[6])
                                serv_notice(target, "Invalid time format")
                                return
                            try:
                                if typetime != 8:
                                    newdigit = int(line[6][:-1])
                                else:
                                    newdigit = 0
                                if isinstance(newdigit, int):
                                    newtime = 0
                                    perma = False
                                    if typetime == 1:
                                        newtime = newdigit
                                    elif typetime == 2:
                                        newtime = newdigit * 60
                                    elif typetime == 3:
                                        newtime = newdigit * 3600
                                    elif typetime == 4:
                                        newtime = newdigit * 86400
                                    elif typetime == 5:
                                        newtime = newdigit * 604800
                                    elif typetime == 6:
                                        newtime = newdigit * 2628000
                                    elif typetime == 7:
                                        newtime = newdigit * 31536000
                                    elif typetime == 8:
                                        newtime = 0
                                        perma = True
                                    account = get_acc(target, userlist)
                                    epoch = int(time.time())
                                    expire = epoch + newtime
                                    #print("%s = %s + %s" % (expire, epoch, newtime))
                                    try:
                                        if line[7]:
                                            arlen = len(line)
                                            i = 7
                                            newstring = ""
                                            while i < arlen:
                                                if newstring == "":
                                                    newstring = line[i]
                                                else:
                                                    newstring = newstring + " " + line[i]
                                                i += 1
                                    except IndexError:
                                        newstring = "No reason specified"
                                    addexempt(target, account, str(theip), epoch, expire, perma, newstring)
                                    #print "IP: " + str(theip) + " .::. account: " + str(account) + " .::. epoch " + str(epoch) + " .::. expire: " + str(expire) + " .::. perma: " + str(perma) + " .::. reason: " + str(newstring) 
                                else:
                                    serv_notice(target, "Invalid time format")
                            except ValueError:
                                serv_notice(target, "Invalid time format")
                        except IndexError:
                            serv_notice(target, "You must provide time for the exemption to be active for")
                    else:
                        serv_notice(target, "You must provide a valid IP address")
                except IndexError:
                    serv_notice(target, "You must provide an IP address to exempt")
            else:
                serv_notice(target, "You lack access to this command.")
        elif line[4].lower() == "del":
            if access_level(target, userlist) >= get_modify_exempt():
                try:
                    if isIP(line[5]) or isIPv6(line[5]):
                        theip = line[5]
                        account = get_acc(target, userlist)
                        delexempt(target, account, theip)
                    else:
                        serv_notice(target, "You must provide a valid IP address")
                except IndexError:
                    serv_notice(target, "You must provide a valid IP address")
            else:
                serv_notice(target, "You lack access to this command.")
        elif line[4].lower() == "list":
            if access_level(target, userlist) >= get_view_exempt():
                exemption_data(target)
            else:
                serv_notice(target, "You lack access to this command.")
        else:
            serv_notice(target, "Invalid paramater for EXEMPT")
    except IndexError:
        serv_notice(target, "Not enough paramaters for EXEMPT")

def say(target, channel, userlist, line):
    if access_level(target, userlist) >= get_say():
        try:
            if line[4]:
                try:
                    if line[5]:
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
            if line[4]:
                try:
                    if line[5]:
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
        if line[4]:
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

def restart(target, userlist, line):
    import os
    try:
        if line[4]:
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
                python = sys.executable
                os.execl(python, python, * sys.argv)
            else:
                serv_notice(target, "You lack access to this command")
    except IndexError:
        serv_notice(target, "Insufficient paramaters for RESTART")

def do_set(target, userlist, line):
    try:
        if line[4]:
            if access_level(target, userlist) >= get_level_req("access_set"):
                if is_settable(line[4]) is True:
                    try:
                        if line[5]:
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

def version(target, userlist):
    if access_level(target, userlist) >= 0:
        import subprocess
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
        serv_notice(target, "POPM authroed ")

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
            if line[4]:
                if line[4].lower() == "threads":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    serv_notice(target, "THREADS displays the current number of worker threads by %s." % (config.BOT_NAME))
                    serv_notice(target, "These threads are spawned when an incoming connection is received")
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
                elif line[4].lower() == "restart":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    serv_notice(target, "RESTART causes POPM to restart while rereading its config.")
                    serv_notice(target, "RESTART takes arguments for the QUIT message and SQUIT reason.")
                    serv_notice(target, "Note: When you use RESTART, your NickServ account")
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
                    serv_notice(target, "restart")
                    serv_notice(target, "setters")
                    serv_notice(target, "say")
                    serv_notice(target, "emote")
                    serv_notice(target, "exempt_mod")
                    serv_notice(target, "exempt_view")
                    serv_notice(target, "")
                    serv_notice(target, "Note: DIE and RESTART use the same access level.")
                    serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "exempt":
                    serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    serv_notice(target, "EXEMPT is the command to view, add, remove, and modify")
                    serv_notice(target, "IP addresses that should be exempt from scanning. This")
                    serv_notice(target, "command can be broken down in to the following:")
                    serv_notice(target, "Viewing the exemption list:")
                    serv_notice(target, "/msg %s EXEMPT LIST" % (config.BOT_NAME))
                    serv_notice(target, "Adding exemptions:")
                    serv_notice(target, "/msg %s EXEMPT ADD 127.0.0.1 30d Services should not be scanned." % (config.BOT_NAME))
                    serv_notice(target, "Removing exemptions:")
                    serv_notice(target, "/msg %s EXEMPT DEL 127.0.0.1" % (config.BOT_NAME))
                    serv_notice(target, "")
                    serv_notice(target, "Notes:")
                    serv_notice(target, "%s will take time arguments such as 1m for 1 minute," % (config.BOT_NAME))
                    serv_notice(target, "1h for 1 hour, 1M for 1 month, 20d for 20 days, 1y for 1 year,")
                    serv_notice(target, "etc. To add a perminant exemption, just use a 0. Example:")
                    serv_notice(target, "/msg %s EXEMPT ADD 127.0.0.1 0 Never scan this address." % (config.BOT_NAME))
                    serv_notice(target, "It is also important to remember that there are two different")
                    serv_notice(target, "access levels between viewing exemptions and modifying the list.")
                    serv_notice(target, "See HELP SET for more details.")
                    serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                else:
                    serv_notice(target, "%s is an unknown command to me." % (line[4]))
        except IndexError:
            if access_level(target, userlist) > 0:
                serv_notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                serv_notice(target, "%s gives authorized users extra control over the proxy monitoring system." % (config.BOT_NAME))
                serv_notice(target, "General commands:")
                serv_notice(target, "Threads:        Shows current number of threads")
                serv_notice(target, "Exempt:         Views/Modifys the exemption list")
                serv_notice(target, "Access:         Shows access for accounts")
                serv_notice(target, "Set:            Sets the configuration for POPM")
                serv_notice(target, "Say:            Makes %s talk" % (config.BOT_NAME))
                serv_notice(target, "Emote:          Makes %s do the equivelent of /me" % (config.BOT_NAME))
                serv_notice(target, "Restart:        Causes POPM to restart")
                serv_notice(target, "Die:            Terminates POPM and disconnects from %s" % (config.NETWORK_NAME))
                serv_notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
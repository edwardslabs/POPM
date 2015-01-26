import datetime
import time
import string
import sys
import config
from access import (
    show_access,
    get_level_req,
    update_access,
    get_acc,
    access_level,
    is_authed,
    my_access
)
from settings import (
    is_settable,
    get_set,
    update_settings,
    get_set_value,
    get_die, get_say,
    addexempt, delexempt,
    get_modify_exempt,
    get_view_exempt,
    exemption_data,
    user_rows,
    exemption_rows_active,
    exemption_rows_inactive,
    claim_root,
    give_root
)
from proxy import isIP, isIPv6
import subprocess
global config
global sys

def privmsg_parser(userlist, line):
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

    elif(command == "uptime"):
        uptime(target, userlist)

    elif(command == "authme"):
        authme(target, userlist, line)

    elif(command == "version"):
        version(target, userlist)

    elif(not channel):
        command_unknown(target, userlist, line)

def get_threads(target, userlist, line):
    if access_level(target, userlist) > 750:
        try:
            config.confproto.notice(target, "There are %s threads running" % (multiprocessing.cpu_count()))
        except NameError:
            config.confproto.notice(target, "There are no threads running")
    elif access_level(target, userlist) <= 749:
        config.confproto.notice(target, "You lack access to this command.")

def get_access(target, userlist, line):
    try:
        access = int(line[5])
        if my_access(target, userlist) == 1000:
            if access <= 1000:
                update_access(line[4], access, target, userlist)
            else:
                config.confproto.notice(target, "Access must be greater than 1000.")
        else:
            config.confproto.notice(target, "Access modification can only be done via root (1000 access) users.")
    except ValueError:
        config.confproto.notice(target, "Access level must be an integer.")
        return
    except IndexError:
        try:
            if my_access(target, userlist) > 0:
                show_access(line[4], target)
        except IndexError:
            if my_access(target, userlist) > 0:
                config.confproto.notice(target, "Account %s has access %s." % (get_acc(target, userlist), access_level(target, userlist)))

def exempt(target, userlist, line):
    try:
        if line[4].lower() == "add":
            if access_level(target, userlist) >= get_modify_exempt():
                try:
                    if isIP(line[5]) or isIPv6(line[5]):
                        theip = line[5]
                        try:
                            try:
                                newdigit = int(line[6][:-1])
                            except ValueError:
                                try:
                                    if int(line[6]) == 0:
                                        newdigit = line[6]
                                    else:
                                        config.confproto.notice(target, "Invalid time format")
                                        return
                                except ValueError:
                                    config.confproto.notice(target, "Invalid time format")
                                    return
                            perma = False
                            if line[6][-1] == "s":
                                newtime = newdigit
                            elif line[6][-1] == "m":
                                newtime = newdigit * 60
                            elif line[6][-1] == "h":
                                newtime = newdigit * 3600
                            elif line[6][-1] == "d":
                                newtime = newdigit * 86400
                            elif line[6][-1] == "w":
                                newtime = newdigit * 604800
                            elif line[6][-1] == "M":
                                newtime = newdigit * 2628000
                            elif line[6][-1] == "y":
                                newtime = newdigit * 31536000
                            elif line[6] == "0":
                                newtime = 0
                                perma = True
                            else:
                                config.confproto.notice(target, "Invalid time format")
                                return
                            account = get_acc(target, userlist)
                            epoch = int(time.time())
                            expire = epoch + newtime
                            try:
                                if line[7]:
                                    newstring = " ".join([line[n] for n in range(7, len(line))])
                            except IndexError:
                                newstring = "No reason specified"
                            addexempt(target, account, str(theip), epoch, expire, perma, newstring)
                        except IndexError:
                            config.confproto.notice(target, "You must provide time for the exemption to be active for")
                    else:
                        config.confproto.notice(target, "You must provide a valid IP address")
                except IndexError:
                    config.confproto.notice(target, "You must provide an IP address to exempt")
            else:
                config.confproto.notice(target, "You lack access to this command.")

        elif line[4].lower() == "del":
            if access_level(target, userlist) >= get_modify_exempt():
                try:
                    if isIP(line[5]) or isIPv6(line[5]):
                        theip = line[5]
                        account = get_acc(target, userlist)
                        delexempt(target, account, theip)
                    else:
                        config.confproto.notice(target, "You must provide a valid IP address")
                except IndexError:
                    config.confproto.notice(target, "You must provide a valid IP address")
            else:
                config.confproto.notice(target, "You lack access to this command.")

        elif line[4].lower() == "list":
            if access_level(target, userlist) >= get_view_exempt():
                exemption_data(target)
            else:
                config.confproto.notice(target, "You lack access to this command.")
        else:
            config.confproto.notice(target, "Invalid paramater for EXEMPT")

    except IndexError:
        config.confproto.notice(target, "Not enough paramaters for EXEMPT")

def say(target, channel, userlist, line):
    if access_level(target, userlist) >= get_say():
        try:
            if line[4]:
                try:
                    if line[5]:
                        if channel and line[4][:1] != "#":
                            taruser = line[2]
                            i = 4
                        else:
                            taruser = line[4]
                            i = 5
                        newstring = " ".join([line[n] for n in range(i, len(line))])
                        config.confproto.privmsg(taruser, "%s" % (newstring))
                except IndexError:
                    if channel and line[4][:1] != "#":
                        taruser = line[2]
                    else:
                        config.confproto.notice(target, "Insufficient paramaters for SAY")
                        return
                    newstring = " ".join([line[n] for n in range(4, len(line))])
                    config.confproto.privmsg(taruser, "%s" % (newstring))
        except IndexError:
                    config.confproto.notice(target, "Insufficient paramaters for SAY")
    else:
        config.confproto.notice(target, "You lack access to this command.")

def emote(target, channel, userlist, line):
    if access_level(target, userlist) >= get_say():
        try:
            if line[4]:
                try:
                    if line[5]:
                        if channel and line[4][:1] != "#":
                            taruser = line[2]
                            i = 4
                        else:
                            taruser = line[4]
                            i = 5
                        newstring = " ".join([line[n] for n in range(i, len(line))])
                        config.confproto.privmsg(taruser, "\001ACTION %s\001" % (newstring))
                except IndexError:
                    if channel and line[4][:1] != "#":
                        taruser = line[2]
                    else:
                        config.confproto.notice(target, "Insufficient paramaters for EMOTE")
                        return
                    newstring = " ".join([line[n] for n in range(4, len(line))])
                    config.confproto.privmsg(taruser, "\001ACTION %s\001" % (newstring))
        except IndexError:
                    config.confproto.notice(target, "Insufficient paramaters for EMOTE.")
    else:
        config.confproto.notice(target, "You lack access to this command.")

def die(target, userlist, line):
    try:
        if line[4]:
            account = get_acc(target, userlist)
            newstring = " ".join([line[n] for n in range(4, len(line))])
            if access_level(target, userlist) >= get_die():
                config.confproto.shutdown(account, newstring)
            else:
                config.confproto.notice(target, "You lack access to this command")
    except IndexError:
        config.confproto.notice(target, "Insufficient paramaters for DIE")

def restart(target, userlist, line):
    try:
        if line[4]:
            account = get_acc(target, userlist)
            newstring = " ".join([line[n] for n in range(4, len(line))])
            if access_level(target, userlist) >= get_die():
                config.confproto.restart(account, newstring)
            else:
                config.confproto.notice(target, "You lack access to this command")
    except IndexError:
        config.confproto.notice(target, "Insufficient paramaters for RESTART")

def authme(target, userlist, line):
    if is_authed(target, userlist):
        if claim_root():
            ourcookie = claim_root()
            try:
                theircookie = int(line[4])
            except ValueError:
                config.confproto.notice(target, "Incorrect authcookie")
            except IndexError:
                config.confproto.notice(target, "You must supply a cookie to identify with")
            if ourcookie == theircookie:
                account = get_acc(target, userlist)
                give_root(account, target)
            else:
                config.confproto.notice(target, "Incorrect authcookie")
        else:
            config.confproto.notice(target, "The authcookie has already been claimed")
    else:
        config.confproto.notice(target, "You must be authenticated with NickServ")

def uptime(target, userlist):
    if access_level(target, userlist) >= get_level_req("access_set"):
        try:
            commit = subprocess.check_output(['git', 'log', '--pretty=format:%h by %ae, %ar', '-1'])
        except:
            commit = "unknown"
        config.confproto.notice(target, "POPM Information:")
        config.confproto.notice(target, "Uptime: %s" % (str(datetime.timedelta(seconds=time.time() - config.main.startTime))))
        config.confproto.notice(target, "PID: %s" % (str(config.main.get_pid())))
        config.confproto.notice(target, "%s" % (config.main.is_forked()))
        config.confproto.notice(target, "Database Backend: %s" % (config.dbtype))
        config.confproto.notice(target, "Users: %s" % (user_rows()))
        config.confproto.notice(target, "Active Exemptions: %s" % (exemption_rows_active()))
        config.confproto.notice(target, "Inactive Exemptions: %s" % (exemption_rows_inactive()))
        config.confproto.notice(target, "POPM version 0.3, latest revision %s." % (commit))
    else:
        config.confproto.notice(target, "You lack access to this command")

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
                                config.confproto.notice(target, "Paramater must be an integer.")
                            if newlevel <= 1000 and newlevel >= 0:
                                update_settings(line[4], newlevel, target)
                            else:
                                config.confproto.notice(target, "Paramater must be an integer between 0 and 1000.")
                    except IndexError:
                        get_set_value(line[4], target)
                else:
                    config.confproto.notice(target, "Invalid SET option.")
            else:
                config.confproto.notice(target, "You lack access to this command.")
    except IndexError:
        if access_level(target, userlist) >= get_level_req("setters"):
            get_set(target)
        else:
            config.confproto.notice(target, "You lack access to this command.")

def version(target, userlist):
    if access_level(target, userlist) >= 0:
        try:
            commit = subprocess.check_output(['git', 'log', '--pretty=format:%h by %ae, %ar', '-1'])
        except:
            commit = "unknown"
        config.confproto.notice(target, "POPM version 0.3, latest revision %s." % (commit))

def command_unknown(target, userlist, line):
    if access_level(target, userlist) > 0:
        newstring = " ".join([line[n] for n in range(3, len(line))])
        config.confproto.notice(target, "Unknown command %s." % (newstring[1:]))

def get_help(target, userlist, line):
    if access_level(target, userlist) > 0:
        try:
            if line[4]:
                if line[4].lower() == "threads":
                    config.confproto.notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    config.confproto.notice(target, "THREADS displays the current number of worker threads by %s." % (config.BOT_NAME))
                    config.confproto.notice(target, "These threads are spawned when an incoming connection is received")
                    config.confproto.notice(target, "to check for proxys on the remote host.")
                    config.confproto.notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "access":
                    config.confproto.notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    config.confproto.notice(target, "ACCESS is a multi-functional command. Access has the ability to")
                    config.confproto.notice(target, "check your access with %s, check other's access, add other users to %s" % (config.BOT_NAME, config.BOT_NAME))
                    config.confproto.notice(target, "and to remove users access to %s. At this time, only root users may" % (config.BOT_NAME))
                    config.confproto.notice(target, "add or remove other users from %s." % (config.BOT_NAME))
                    config.confproto.notice(target, "Note: To remove a users access, set their access to -1")
                    config.confproto.notice(target, "Examples:")
                    config.confproto.notice(target, "/msg %s ACCESS foobar" % (config.BOT_NAME))
                    config.confproto.notice(target, "/msg %s ACCESS *" % (config.BOT_NAME))
                    config.confproto.notice(target, "/msg %s ACCESS foo 950" % (config.BOT_NAME))
                    config.confproto.notice(target, "/msg %s ACCESS bar -1" % (config.BOT_NAME))
                    config.confproto.notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "die":
                    config.confproto.notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    config.confproto.notice(target, "DIE causes %s to quit and POPM to disconnect from %s." % (config.BOT_NAME, config.NETWORK_NAME))
                    config.confproto.notice(target, "This will completly stop the program and will have to")
                    config.confproto.notice(target, "be restarted locally. DIE takes arguments for the QUIT message")
                    config.confproto.notice(target, "and SQUIT reason. Note: When you use DIE, your NickServ account")
                    config.confproto.notice(target, "name will be attached to the SQUIT message.")
                    config.confproto.notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "restart":
                    config.confproto.notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    config.confproto.notice(target, "RESTART causes POPM to restart while rereading its config.")
                    config.confproto.notice(target, "RESTART takes arguments for the QUIT message and SQUIT reason.")
                    config.confproto.notice(target, "Note: When you use RESTART, your NickServ account")
                    config.confproto.notice(target, "name will be attached to the SQUIT message.")
                    config.confproto.notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "say":
                    config.confproto.notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    config.confproto.notice(target, "/msg %s SAY <#channel|nick> <text>" % (config.BOT_NAME))
                    config.confproto.notice(target, "Makes %s send a message to a specified nick/channel." % (config.BOT_NAME))
                    config.confproto.notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "emote":
                    config.confproto.notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    config.confproto.notice(target, "/msg %s EMOTE <#channel|nick> <text>" % (config.BOT_NAME))
                    config.confproto.notice(target, "Makes %s do the equivelent of /me to the specified nick/channel." % (config.BOT_NAME))
                    config.confproto.notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "uptime":
                    config.confproto.notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    config.confproto.notice(target, "UPTIME will display current running information on POPM.")
                    config.confproto.notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "set":
                    config.confproto.notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    config.confproto.notice(target, "SET on its own will display the current configuration")
                    config.confproto.notice(target, "for %s. Note, that the SET command can only be used by" % (config.BOT_NAME))
                    config.confproto.notice(target, "users with SET access. SET can also take arguments.")
                    config.confproto.notice(target, "Below is a list of items you can set in %s" % (config.BOT_NAME))
                    config.confproto.notice(target, "To change any of the settings, just type")
                    config.confproto.notice(target, "/msg %s SET paramter value" % (config.BOT_NAME))
                    config.confproto.notice(target, "")
                    config.confproto.notice(target, "Examples:")
                    config.confproto.notice(target, "/msg %s SET DNSBL off" % (config.BOT_NAME))
                    config.confproto.notice(target, "/msg %s SET HTTP on" % (config.BOT_NAME))
                    config.confproto.notice(target, "/msg %s SET SOCKS on" % (config.BOT_NAME))
                    config.confproto.notice(target, "/msg %s SET SETTERS 900" % (config.BOT_NAME))
                    config.confproto.notice(target, "/msg %s SET DIE 1000" % (config.BOT_NAME))
                    config.confproto.notice(target, "")
                    config.confproto.notice(target, "ON/OFF Set Options:")
                    config.confproto.notice(target, "http")
                    config.confproto.notice(target, "socks")
                    config.confproto.notice(target, "dnsbl")
                    config.confproto.notice(target, "Access Level Set Options:")
                    config.confproto.notice(target, "die")
                    config.confproto.notice(target, "restart")
                    config.confproto.notice(target, "setters")
                    config.confproto.notice(target, "say")
                    config.confproto.notice(target, "emote")
                    config.confproto.notice(target, "exempt_mod")
                    config.confproto.notice(target, "exempt_view")
                    config.confproto.notice(target, "")
                    config.confproto.notice(target, "Note: DIE and RESTART use the same access level.")
                    config.confproto.notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                elif line[4].lower() == "exempt":
                    config.confproto.notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                    config.confproto.notice(target, "EXEMPT is the command to view, add, remove, and modify")
                    config.confproto.notice(target, "IP addresses that should be exempt from scanning. This")
                    config.confproto.notice(target, "command can be broken down in to the following:")
                    config.confproto.notice(target, "Viewing the exemption list:")
                    config.confproto.notice(target, "/msg %s EXEMPT LIST" % (config.BOT_NAME))
                    config.confproto.notice(target, "Adding exemptions:")
                    config.confproto.notice(target, "/msg %s EXEMPT ADD 127.0.0.1 30d Services should not be scanned." % (config.BOT_NAME))
                    config.confproto.notice(target, "Removing exemptions:")
                    config.confproto.notice(target, "/msg %s EXEMPT DEL 127.0.0.1" % (config.BOT_NAME))
                    config.confproto.notice(target, "")
                    config.confproto.notice(target, "Notes:")
                    config.confproto.notice(target, "%s will take time arguments such as 1m for 1 minute," % (config.BOT_NAME))
                    config.confproto.notice(target, "1h for 1 hour, 1M for 1 month, 20d for 20 days, 1y for 1 year,")
                    config.confproto.notice(target, "etc. To add a perminant exemption, just use a 0. Example:")
                    config.confproto.notice(target, "/msg %s EXEMPT ADD 127.0.0.1 0 Never scan this address." % (config.BOT_NAME))
                    config.confproto.notice(target, "It is also important to remember that there are two different")
                    config.confproto.notice(target, "access levels between viewing exemptions and modifying the list.")
                    config.confproto.notice(target, "See HELP SET for more details.")
                    config.confproto.notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
                else:
                    config.confproto.notice(target, "%s is an unknown command to me." % (line[4]))
        except IndexError:
            if access_level(target, userlist) > 0:
                config.confproto.notice(target, "-=-=-=-=-=-=- %s Help -=-=-=-=-=-=-" % (config.BOT_NAME))
                config.confproto.notice(target, "%s gives authorized users extra control over the proxy monitoring system." % (config.BOT_NAME))
                config.confproto.notice(target, "General commands:")
                config.confproto.notice(target, "Threads:        Shows current number of threads")
                config.confproto.notice(target, "Exempt:         Views/Modifys the exemption list")
                config.confproto.notice(target, "Access:         Shows access for accounts")
                config.confproto.notice(target, "Set:            Sets the configuration for POPM")
                config.confproto.notice(target, "Say:            Makes %s talk" % (config.BOT_NAME))
                config.confproto.notice(target, "Emote:          Makes %s do the equivelent of /me" % (config.BOT_NAME))
                config.confproto.notice(target, "Uptime:         Show statistics on POPM.")
                config.confproto.notice(target, "Restart:        Causes POPM to restart")
                config.confproto.notice(target, "Die:            Terminates POPM and disconnects from %s" % (config.NETWORK_NAME))
                config.confproto.notice(target, "-=-=-=-=-=-=- End Of Help -=-=-=-=-=-=-")
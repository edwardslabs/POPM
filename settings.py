import config
global config

def is_settable(param):
    param = param.lower()
    if (param == "dnsbl"
        or param == "http"
        or param == "socks"
        or param == "die"
        or param == "restart"
        or param == "set"
        or param == "setters"
        or param == "http_connect"
        or param == "emote"
        or param == "say"
        or param == "exempt_mod"
        or param == "exempt_view"):
        return True
    return False

def get_set(target):
    from commands import serv_notice
    config.cur.execute("SELECT * FROM settings")
    serv_notice(target, "Current configuration settings:")
    for row in config.cur.fetchall():
        serv_notice(target, "DNSBL Scans:                   %s" % (row[0]))
        serv_notice(target, "HTTP_CONNECT Scans:     %s" % (row[1]))
        serv_notice(target, "SOCKS Scans:                   %s" % (row[2]))
        serv_notice(target, "Die/Restart access:            %s" % (row[3]))
        serv_notice(target, "Setters level:                     %s" % (row[4]))
        serv_notice(target, "Say access:                       %s" % (row[5]))
        serv_notice(target, "Emote access:                    %s" % (row[6]))
        serv_notice(target, "View Exempts:                    %s" % (row[7]))
        serv_notice(target, "Modify Exempts:                  %s" % (row[8]))
    serv_notice(target, "End of configuration.")

def update_settings(param, newlevel, target):
    from commands import serv_notice
    import sys
    newlevel = int(newlevel)
    if param == "dnsbl":
        param = "enable_dnsbl"
        fancy = "DNSBL Scans"
    elif param == "http" or param == "http_connect":
        param = "enable_http"
        fancy = "HTTP_CONNECT Scans"
    elif param == "socks":
        param = "enable_socks"
        fancy = "SOCKS Scans"
    elif param == "die" or param == "restart":
        param = "access_die"
        fancy = "Die/Restart access"
    elif param == "set" or param == "setters":
        param = "access_set"
        fancy = "Setters"
    elif param == "emote":
        param = "access_emote"
        fancy = "Emote"
    elif param == "say":
        param = "access_say"
        fancy = "say"
    elif param == "exempt_mod":
        param = "modify_exempts"
        fancy = "Exempt modifiers"
    elif param == "exempt_view":
        param = "view_exempts"
        fancy = "Exempt viewers"

    if param == "enable_dnsbl" or param == "enable_socks" or param == "enable_http":
        if newlevel > 1 or newlevel < 0:
            serv_notice(target, "%s must be either ON or OFF." % (fancy))
        else:
             if newlevel == 1:
                 newlevel = True
                 fancyonoff = "on"
             else:
                 newlevel = False
                 fancyonoff = "off"
             config.cur.execute("UPDATE settings SET %s = %s" % (param, newlevel))
             config.pgconn.commit()
             config.cur.execute("SELECT * from settings")
             print "Updated settings"
             try:
                 for row in config.cur.fetchall():
                     ENABLE_DNSBL = row[0]
                     ENABLE_HTTP = row[1]
                     ENABLE_SOCKS = row[2]
                 serv_notice(target, "%s has been set to %s." % (fancy, fancyonoff))
             except:
                 print "ERROR! [%s %s]" % (sys.exc_info()[0], sys.exc_info()[0])
                 serv_notice(target, "A fatal error has occured changing %s to %s. Please send this message to the developers: %s %s" % (fancy, fancyonoff, sys.exc_info()[0], sys.exc_info()[1]))
    else:
         config.cur.execute("UPDATE settings SET %s = %s" % (param, newlevel))
         config.pgconn.commit()
         config.cur.execute("SELECT enable_dnsbl,enable_http,enable_socks,access_die,access_set FROM settings")
         for row in config.cur.fetchall():
             ENABLE_DNSBL = row[0]
             ENABLE_HTTP = row[1]
             ENABLE_SOCKS = row[2]
         print "Updated settings"
         serv_notice(target, "%s has been set to %s." % (fancy, newlevel))

def get_set_value(param, target):
    from commands import serv_notice
    if param == "dnsbl":
        param = "enable_dnsbl"
        fancy = "DNSBL Scans"
    elif param == "http" or param == "http_connect":
        param = "enable_http"
        fancy = "HTTP_CONNECT Scans"
    elif param == "socks":
        param = "enable_socks"
        fancy = "SOCKS Scans"
    elif param == "die" or param == "restart":
        param = "access_die"
        fancy = "Die/Restart access"
    elif param == "set" or param == "setters":
        param = "access_set"
        fancy = "Setters"
    elif param == "say" or param == "emote":
        param = "access_say"
        fancy = "Say/Emote"
    config.cur.execute("SELECT %s FROM settings" % (param))
    item = config.cur.fetchone()
    serv_notice(target, "%s is set to %s." % (fancy, item[0]))

def get_die():
    config.cur.execute("SELECT access_die FROM settings")
    value = config.cur.fetchone()
    return value[0]

def get_say():
    config.cur.execute("SELECT access_say FROM settings")
    value = config.cur.fetchone()
    return value[0]

def get_view_exempt():
    config.cur.execute("SELECT view_exempts FROM settings")
    value = config.cur.fetchone()
    return value[0]

def get_modify_exempt():
    config.cur.execute("SELECT modify_exempts FROM settings")
    value = config.cur.fetchone()
    return value[0]

def get_dnsbl_value():
    config.curauto.execute("SELECT enable_dnsbl FROM settings")
    value = config.curauto.fetchone()
    return value[0]

def get_http_value():
    config.curauto.execute("SELECT enable_http FROM settings")
    value = config.curauto.fetchone()
    return value[0]

def get_socks_value():
    config.curauto.execute("SELECT enable_socks FROM settings")
    value = config.curauto.fetchone()
    return value[0]

def isExempt(trueIP):
    config.curauto.execute("SELECT ip FROM exemptions WHERE ip = %s", [trueIP])
    if config.curauto.rowcount > 0:
        #print "%s is exempt" % (trueIP)
        return True
    #print "%s is NOT exempt" % (trueIP)
    return False

def checkexpired():
    from commands import serv_privmsg
    import time
    epoch = int(time.time())
    config.curauto.execute("SELECT ip FROM exemptions WHERE expires <= %s AND active = '1' AND perma = '0'", [epoch])
    if config.curauto.rowcount > 0:
        for row in config.curauto.fetchall():
            serv_privmsg(config.DEBUG_CHANNEL, "%s's exemption period has expired" % (row[0]))
    config.curauto.execute("UPDATE exemptions SET active = '0' WHERE expires <= %s AND active = '1' AND perma = '0'", [epoch])
    config.pgconnauto.commit()

def addexempt(target, account, theip, epoch, expire, perma, reason):
    from commands import serv_notice
    if perma == True:
        value = 1
    else:
        value = 0
    config.cur.execute("SELECT ip FROM exemptions WHERE ip = %s AND active = '1'", [theip])
    if config.cur.rowcount > 0:
        config.cur.execute("UPDATE exemptions SET wholast = %s, lastmodified = %s, expires = %s, perma = %s, reason = %s WHERE ip = %s", (account, epoch, expire, perma, reason, theip))
        config.pgconn.commit()
        serv_notice(target, "Updated exemption record for %s" % (theip))
    else:
        config.cur.execute("INSERT INTO exemptions (ip,whenadded,whoadded,expires,perma,reason,active) VALUES (%s, %s, %s, %s, %s, %s, '1')", (theip, epoch, account, expire, perma, reason))
        config.pgconn.commit()
        serv_notice(target, "Added %s to the exemption list." % (theip))

def delexempt(target, account, theip):
    from commands import serv_notice
    config.cur.execute("SELECT ip FROM exemptions WHERE ip = %s AND active = '1'", [theip])
    if config.cur.rowcount > 0:
        config.cur.execute("UPDATE exemptions SET active = '0' WHERE ip = %s", [theip])
        config.pgconn.commit()
        serv_notice(target, "Removed %s from the proxy exemption list." % (theip))
    else:
        serv_notice(target, "%s is not an exempted IP address." % (theip))

def exemption_data(target):
    from commands import serv_notice
    import time
    config.cur.execute("SELECT * FROM exemptions WHERE active = '1'")
    if config.cur.rowcount > 0:
        serv_notice(target, "Exempted IP address:")
        for row in config.cur.fetchall():
            if row[7] == '0':
                if row[4] is None:
                    serv_notice(target, "ID: %d | IP %s - Added %s by %s set to expire %s for reason %s." % (row[0], row[1], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[2])), row[3], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[5])), row[8]))
                else:
                    serv_notice(target, "ID: %d | IP %s - Added %s by %s set to expire %s for reason %s. Last modified by %s on %s" % (row[0], row[1], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[2])), row[3], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[5])), row[8], row[6], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[4]))))
            else:
                if row[4] is None:
                    serv_notice(target, "ID: %d | IP %s - Perminantly added on %s by %s for reason %s." % (row[0], row[1], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[2])), row[3], row[8]))
                else:
                    serv_notice(target, "ID: %d | IP %s - Perminantly added on %s by %s for reason %s. Last modified by %s on %s" % (row[0], row[1], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[2])), row[3], row[8], row[6], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[4]))))
    else:
        serv_notice(target, "There are no active exemptions at this time.")
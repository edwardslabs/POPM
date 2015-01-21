import config
global config

def is_settable(param):
    param = param.lower()
    if (param == "dnsbl"
    or param == "http"
    or param == "socks"
    or param == "die"
    or param == "set"
    or param == "setters"
    or param == "http_connect"
    or param == "emote"
    or param == "say"):
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
        serv_notice(target, "Die access:                        %s" % (row[3]))
        serv_notice(target, "Setters level:                     %s" % (row[4]))
        serv_notice(target, "Say access:                     %s" % (row[5]))
        serv_notice(target, "Emote access:                     %s" % (row[6]))
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
    elif param == "die":
        param = "access_die"
        fancy = "Die access"
    elif param == "set" or param == "setters":
        param = "access_set"
        fancy = "Setters"
    elif param == "emote":
        param = "access_emote"
        fancy = "Emote"
    elif param == "say":
        param = "access_say"
        fancy = "say"

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
    elif param == "die":
        param = "access_die"
        fancy = "Die access"
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
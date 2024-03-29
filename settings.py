import config
import datetime
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
    config.cur.execute("SELECT * FROM settings")
    config.confproto.notice(target, "Current configuration settings:")
    for row in config.cur.fetchall():
        config.confproto.notice(target, "DNSBL Scans:                   %s" % (row[0]))
        config.confproto.notice(target, "HTTP_CONNECT Scans:     %s" % (row[1]))
        config.confproto.notice(target, "SOCKS Scans:                   %s" % (row[2]))
        config.confproto.notice(target, "Die/Restart access:            %s" % (row[3]))
        config.confproto.notice(target, "Setters level:                     %s" % (row[4]))
        config.confproto.notice(target, "Say access:                       %s" % (row[5]))
        config.confproto.notice(target, "Emote access:                    %s" % (row[6]))
        config.confproto.notice(target, "View Exempts:                    %s" % (row[7]))
        config.confproto.notice(target, "Modify Exempts:                  %s" % (row[8]))
    config.confproto.notice(target, "End of configuration.")

def update_settings(param, newlevel, target):
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
        fancy = "Say/Emote"
    elif param == "say":
        param = "access_say"
        fancy = "Say/Emote"
    elif param == "exempt_mod":
        param = "modify_exempts"
        fancy = "Exempt modifiers"
    elif param == "exempt_view":
        param = "view_exempts"
        fancy = "Exempt viewers"

    if param == "enable_dnsbl" or param == "enable_socks" or param == "enable_http":
        if newlevel > 1 or newlevel < 0:
            config.confproto.notice(target, "%s must be either ON or OFF." % (fancy))
        else:
            if newlevel == 1:
                if config.dbtype == "SQLite":
                    newlevel = 1
                else:
                    newlevel = True
                fancyonoff = "on"
            else:
                if config.dbtype == "SQLite":
                    newlevel = 0
                else:
                    newlevel = False
                fancyonoff = "off"
            if config.dbtype == "SQLite":
                config.cur.execute("UPDATE settings SET %s = %s" % (param, newlevel))
            else:
                config.cur.execute("UPDATE settings SET %s = %s" % (param, newlevel))
            config.dbconn.commit()
            config.confproto.notice(target, "%s has been set to %s." % (fancy, fancyonoff))
    else:
        if config.dbtype == "SQLite":
            config.cur.execute("UPDATE settings SET %s = %s" % (param, newlevel))
        else:
            config.cur.execute("UPDATE settings SET %s = %s" % (param, newlevel))
        config.dbconn.commit()
        config.confproto.notice(target, "%s has been set to %s." % (fancy, newlevel))

def get_set_value(param, target):
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
    if config.dbtype == "SQLite":
        config.cur.execute("SELECT %s FROM settings" % param)
    else:
        config.cur.execute("SELECT %s FROM settings" % (param))
    item = config.cur.fetchone()
    value = item[0]
    if param == "enable_socks" or param == "enable_http" or param == "enable_dnsbl":
        if value == 1 or value == True:
            value = "On"
        else:
            value = "Off"
    config.confproto.notice(target, "%s is set to %s." % (fancy, value))

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
    if config.dbtype == "SQLite":
        config.curauto.execute("SELECT ip FROM exemptions WHERE ip = ?", [trueIP])
    else:
        config.curauto.execute("SELECT ip FROM exemptions WHERE ip = %s", [trueIP])
    if config.curauto.rowcount > 0:
        return True
    return False

def checkexpired():
    import time
    epoch = int(time.time())
    if config.dbtype == "SQLite":
        config.curauto.execute("SELECT COUNT(*) FROM exemptions WHERE expires <= ? AND active = '1' AND perma = '0'", [epoch])
        value = config.curauto.fetchone()
        if value[0] > 0:
            config.curauto.execute("SELECT ip FROM exemptions WHERE expires <= ? AND active = '1' AND perma = '0'", [epoch])
            for row in config.curauto.fetchall():
                config.confproto.privmsg(config.DEBUG_CHANNEL, "%s's exemption period has expired" % (row[0]))
            config.curauto.execute("UPDATE exemptions SET active = '0' WHERE expires <= ? AND active = '1' AND perma = '0'", [epoch])
    else:
        config.curauto.execute("SELECT ip FROM exemptions WHERE expires <= %s AND active = '1' AND perma = '0'", [epoch])
        if config.curauto.rowcount > 0:
            config.curauto.execute("SELECT ip FROM exemptions WHERE expires <= %s AND active = '1' AND perma = '0'", [epoch])
            for row in config.curauto.fetchall():
                config.confproto.privmsg(config.DEBUG_CHANNEL, "%s's exemption period has expired" % (row[0]))
            config.curauto.execute("UPDATE exemptions SET active = '0' WHERE expires <= %s AND active = '1' AND perma = '0'", [epoch])
            config.dbconnauto.commit()

def addexempt(target, account, theip, epoch, expire, perma, reason, newtime):
    if perma == True:
        valueperm = 1
    else:
        valueperm = 0
    if config.dbtype == "SQLite":
        config.cur.execute("SELECT COUNT(*) FROM exemptions WHERE ip = ? AND active = '1'", [theip])
        value = config.cur.fetchone()
        if value[0] > 0:
            config.cur.execute("UPDATE exemptions SET wholast = ?, lastmodified = ?, expires = ?, perma = ?, reason = ? WHERE ip = ?", (account, epoch, expire, valueperm, reason, theip))
            if valueperm == 1:
                config.confproto.notice(target, "Updated exemption record for %s to never expire." % (theip))
            else:
                config.confproto.notice(target, "Updated exemption record for %s to expire in %s." % (theip, str(datetime.timedelta(seconds=newtime))))
        else:
            config.cur.execute("INSERT INTO exemptions (ip,whenadded,whoadded,expires,perma,reason,active) VALUES (?, ?, ?, ?, ?, ?, '1')", (theip, epoch, account, expire, valueperm, reason))
            if valueperm == 1:
                config.confproto.notice(target, "Permanently added %s to the exemption list." % (theip))
            else:
                config.confproto.notice(target, "Added %s to the exemption list for %s" % (theip, str(datetime.timedelta(seconds=newtime))))
    else:
        config.cur.execute("SELECT ip FROM exemptions WHERE ip = %s AND active = '1'", [theip])
        if config.cur.rowcount > 0:
            config.cur.execute("UPDATE exemptions SET wholast = %s, lastmodified = %s, expires = %s, perma = %s, reason = %s WHERE ip = %s", (account, epoch, expire, perma, reason, theip))
            config.dbconn.commit()
            if valueperm == 1:
                config.confproto.notice(target, "Updated exemption record for %s to never expire." % (theip))
            else:
                config.confproto.notice(target, "Updated exemption record for %s to expire in %s." % (theip, str(datetime.timedelta(seconds=newtime))))
        else:
            config.cur.execute("INSERT INTO exemptions (ip,whenadded,whoadded,expires,perma,reason,active) VALUES (%s, %s, %s, %s, %s, %s, '1')", (theip, epoch, account, expire, perma, reason))
            config.dbconn.commit()
            if valueperm == 1:
                config.confproto.notice(target, "Permanently added %s to the exemption list." % (theip))
            else:
                config.confproto.notice(target, "Added %s to the exemption list for %s" % (theip, str(datetime.timedelta(seconds=newtime))))

def delexempt(target, account, theip):
    if config.dbtype == "SQLite":
        config.cur.execute("SELECT COUNT(*) FROM exemptions WHERE ip = ? AND active = '1'", [theip])
        value = config.cur.fetchone()
        if value[0] > 0:
            config.cur.execute("UPDATE exemptions SET active = '0' WHERE ip = ?", [theip])
            config.confproto.notice(target, "Removed %s from the proxy exemption list." % (theip))
        else:
            config.confproto.notice(target, "%s is not an exempted IP address." % (theip))
    else:
        config.cur.execute("SELECT ip FROM exemptions WHERE ip = %s AND active = '1'", [theip])
        if config.cur.rowcount > 0:
            config.cur.execute("UPDATE exemptions SET active = '0' WHERE ip = %s", [theip])
            config.dbconn.commit()
            config.confproto.notice(target, "Removed %s from the proxy exemption list." % (theip))
        else:
            config.confproto.notice(target, "%s is not an exempted IP address." % (theip))

def exemption_data(target):
    import time
    config.cur.execute("SELECT COUNT(*) FROM exemptions WHERE active = '1'")
    value = config.cur.fetchone()
    if value[0] > 0:
        config.confproto.notice(target, "Exempted IP address:")
        config.cur.execute("SELECT * FROM exemptions WHERE active = '1'")
        for row in config.cur.fetchall():
            if not row[7]:
                if row[4] is None:
                    config.confproto.notice(target, "ID: %d | IP %s - Added %s by %s set to expire %s for reason %s." % (row[0], row[1], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[2])), row[3], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[5])), row[8]))
                else:
                    config.confproto.notice(target, "ID: %d | IP %s - Added %s by %s set to expire %s for reason %s. Last modified by %s on %s" % (row[0], row[1], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[2])), row[3], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[5])), row[8], row[6], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[4]))))
            else:
                if row[4] is None:
                    config.confproto.notice(target, "ID: %d | IP %s - Permanently added on %s by %s for reason %s." % (row[0], row[1], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[2])), row[3], row[8]))
                else:
                    config.confproto.notice(target, "ID: %d | IP %s - Permanently added on %s by %s for reason %s. Last modified by %s on %s" % (row[0], row[1], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[2])), row[3], row[8], row[6], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[4]))))
    else:
        config.confproto.notice(target, "There are no active exemptions at this time.")

def user_rows():
    config.cur.execute("SELECT COUNT(*) FROM users")
    value = config.cur.fetchone()
    return value[0]

def exemption_rows_active():
    config.cur.execute("SELECT COUNT(*) FROM exemptions WHERE active = '1'")
    value = config.cur.fetchone()
    return value[0]

def exemption_rows_inactive():
    config.cur.execute("SELECT COUNT(*) FROM exemptions WHERE active = '0'")
    value = config.cur.fetchone()
    return value[0]

def claim_root():
    import string
    config.cur.execute("SELECT COUNT(*) FROM users")
    value = config.cur.fetchone()
    if value[0] == 1:
        config.cur.execute("SELECT admin FROM users LIMIT 1")
        uid = config.cur.fetchone()
        if uid[0].isdigit():
            return int(uid[0])
        else:
            return False
    else:
        return False

def give_root(account, target):
    if config.dbtype == "SQLite":
        config.cur.execute("UPDATE users SET admin = ?", [account])
    else:
        config.cur.execute("UPDATE users SET admin = %s", [account])
    config.confproto.notice(target, "Thanks! Your account (%s) now has root privieleges to POPM." % (account))
    config.confproto.notice(target, "For assistance, you may /msg %s HELP or consult the README file." % (config.BOT_NAME))
    config.dbconn.commit()
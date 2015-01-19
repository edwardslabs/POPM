def is_settable(param):
    if param.lower() == "dnsbl" or param.lower() == "http" or param.lower() == "socks" or param.lower() == "die" or param.lower() == "set" or param.lower() == "setters" or param.lower() == "http_connect":
        return True
    return False

def get_set(target):
    from config import *
    from bot import *
    from server import *
    cur.execute("SELECT enable_dnsbl,enable_http,enable_socks,access_die,access_set FROM settings")
    s.send("%sAAA O %s :Current configuration settings:\n" % (SERVER_NUMERIC, target))
    for row in cur.fetchall():
        s.send("%sAAA O %s :DNSBL Scans:                   %s\n" % (SERVER_NUMERIC, target, row[0]))
        s.send("%sAAA O %s :HTTP_CONNECT Scans:     %s\n" % (SERVER_NUMERIC, target, row[1]))
        s.send("%sAAA O %s :SOCKS Scans:                   %s\n" % (SERVER_NUMERIC, target, row[2]))
        s.send("%sAAA O %s :Die access:                        %s\n" % (SERVER_NUMERIC, target, row[3]))
        s.send("%sAAA O %s :Setters level:                     %s\n" % (SERVER_NUMERIC, target, row[4]))
    s.send("%sAAA O %s :End of configuration.\n" % (SERVER_NUMERIC, target))

def update_settings(param, newlevel, target):
    from config import *
    from bot import *
    from server import *
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

    if param == "enable_dnsbl" or param == "enable_socks" or param == "enable_http":
        if newlevel > 1 or newlevel < 0:
            s.send("%sAAA O %s :%s must be either ON or OFF.\n" % (SERVER_NUMERIC, target, fancy))
        else:
             if newlevel == 1:
                 newlevel = True
                 fancyonoff = "on"
             else:
                 newlevel = False
                 fancyonoff = "off"
                 escparam = "'" + str(param) + "'"
                 escnewlevel = "'" + str(newlevel) + "'"
             cur.execute("UPDATE settings SET %s = %s" % (escparam, escnewlevel))
             pgconn.commit()
             cur.execute("SELECT * from settings")
             print "Updated settings"
             try:
                 for row in cur.fetchall():
                     ENABLE_DNSBL = row[0]
                     ENABLE_HTTP = row[1]
                     ENABLE_SOCKS = row[2]
                 s.send("%sAAA O %s :%s has been set to %s.\n" % (SERVER_NUMERIC, target, fancy, fancyonoff))
             except:
                 print "ERROR! [%s %s]" % (sys.exc_info()[0], sys.exc_info()[0])
                 s.send("%sAAA O %s :A fatal error has occured changing %s to %s. Please send this message to the developers: %s %s\n" % (SERVER_NUMERIC, target, fancy, fancyonoff, sys.exc_info()[0], sys.exc_info()[1]))
    else:
         escparam = "'" + str(param) + "'"
         escnewlevel = "'" + str(newlevel) + "'"
         cur.execute("UPDATE settings SET %s = %s" % (escparam, escnewlevel))
         pgconn.commit()
         cur.execute("SELECT enable_dnsbl,enable_http,enable_socks,access_die,access_set FROM settings")
         for row in cur.fetchall():
             ENABLE_DNSBL = row[0]
             ENABLE_HTTP = row[1]
             ENABLE_SOCKS = row[2]
         print "Updated settings"
         s.send("%sAAA O %s :%s has been set to %s\n" % (SERVER_NUMERIC, target, fancy, newlevel))

def get_set_value(param, target):
    from config import *
    from bot import *
    from server import *
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
        escparam = "'" + str(param) + "'"
    cur.execute("SELECT %s FROM settings" % (escparam))
    for row in cur.fetchall():
        s.send("%sAAA O %s :%s is set to %s\n" % (SERVER_NUMERIC, target, fancy, row[0]))
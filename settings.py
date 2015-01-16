class DBSettings:
    def is_settable(self, param):
        if param.lower() == "dnsbl" or param.lower() == "http" or param.lower() == "socks" or param.lower() == "die" or param.lower() == "set" or param.lower() == "setters" or param.lower() == "http_connect":
            return True
        return False

    def get_set(self, target):
        import server
        import config
        import database
        DB = database.Database()
        config = config.Config()
        conn = server.Server()
        DB.cur.execute("SELECT enable_dnsbl,enable_http,enable_socks,access_die,access_set FROM settings")
        s.send("%sAAA O %s :Current configuration settings:\n" % (SERVER_NUMERIC, target))
        for row in DB.cur.fetchall():
            s.send("%sAAA O %s :DNSBL Scans:                   %s\n" % (SERVER_NUMERIC, target, row[0]))
            s.send("%sAAA O %s :HTTP_CONNECT Scans:     %s\n" % (SERVER_NUMERIC, target, row[1]))
            s.send("%sAAA O %s :SOCKS Scans:                   %s\n" % (SERVER_NUMERIC, target, row[2]))
            s.send("%sAAA O %s :Die access:                        %s\n" % (SERVER_NUMERIC, target, row[3]))
            s.send("%sAAA O %s :Setters level:                     %s\n" % (SERVER_NUMERIC, target, row[4]))
        s.send("%sAAA O %s :End of configuration.\n" % (SERVER_NUMERIC, target))

    def update_settings(self, param, newlevel, target):
        import server
        import config
        import database
        DB = database.Database()
        config = config.Config()
        conn = server.Server()
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
                 DB.cur.execute("UPDATE settings SET %s = %s" % (param, newlevel))
                 pgconn.commit()
                 print "Updated settings"
                 s.send("%sAAA O %s :%s has been set to %s.\n" % (SERVER_NUMERIC, target, fancy, fancyonoff))
        else:
             DB.cur.execute("UPDATE settings SET %s = %d" % (param, newlevel))
             pgconn.commit()
             print "Updated settings"
             s.send("%sAAA O %s :%s has been set to %s\n" % (SERVER_NUMERIC, target, fancy, newlevel))

    def get_set_value(self, param, target):
        import server
        import config
        import database
        DB = database.Database()
        config = config.Config()
        conn = server.Server()
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
        DB.cur.execute("SELECT %s FROM settings" % (param))
        for row in DB.cur.fetchall():
            s.send("%sAAA O %s :%s is set to %s\n" % (SERVER_NUMERIC, target, fancy, row[0]))
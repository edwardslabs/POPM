class DNSBL:
    def DNSBL(self, ip, nick):
        import database
        import isip
        import http_connect
        htt = http_connect.httpcon
        db = database.Database()
        ipcheck = isip.confirmIP()
        db.curauto.execute("SELECT enable_dnsbl,enable_http,enable_socks,access_die,access_set FROM settings")
        for row in db.curauto.fetchall():
            self.ENABLE_DNSBL = row[0]
            self.ENABLE_HTTP = row[1]
            self.ENABLE_SOCKS = row[2]
            self.ACCESS_DIE = row[3]
            self.ACCESS_SET = row[4]
        bll = ["tor.dan.me.uk", "rbl.efnetrbl.org", "dnsbl.proxybl.org", "dnsbl.dronebl.org", "tor.efnet.org"]
        if ipcheck.isIP(ip) is False:
            answers = dns.resolver.query(ip,'A')
            for server in answers:
                rawip = server
        else:
            rawip = ip

        rawip = str(rawip)

        if self.ENABLE_DNSBL == 0:
            htt.http_connect(rawip)
        else:

            newip = rawip.split(".")
            newip = newip[::-1]
            newip = '.'.join(newip)

            for blacklist in bll:
                newstring = newip + "." + blacklist
                try:
                    answers = dns.resolver.query(newstring,'A')
                    if answers != False:
                        s.send("%s GL * +*@%s 259200 %d %d :AUTO Your IP is listed as being an infected drone, or otherwise not fit to join %s. [Detected %s]\n" % (SERVER_NUMERIC, rawip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, blacklist))
                        print("[WRITE][DNSBL_FOUND]: %s GL * +*@%s 259200 %d %d :AUTO Your IP is listed as being an infected drone, or otherwise not fit to join %s. [Detected %s]" % (SERVER_NUMERIC, rawip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, blacklist))
                        break
                except dns.resolver.NXDOMAIN:
                    continue

            htt.http_connect(rawip)
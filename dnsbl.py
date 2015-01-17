def DNSBL(ip, nick):
    from server import *
    from bot import *
    from config import *
    from http_connect import *
    from isip import isIP
    curauto.execute("SELECT enable_dnsbl,enable_http,enable_socks,access_die,access_set FROM settings")
    for row in curauto.fetchall():
        ENABLE_DNSBL = row[0]
        ENABLE_HTTP = row[1]
        ENABLE_SOCKS = row[2]
        ACCESS_DIE = row[3]
        ACCESS_SET = row[4]
    bll = ["tor.dan.me.uk", "rbl.efnetrbl.org", "dnsbl.proxybl.org", "dnsbl.dronebl.org", "tor.efnet.org"]
    if isIP(ip) is False:
        answers = dns.resolver.query(ip,'A')
        for server in answers:
            rawip = server
    else:
        rawip = ip

    rawip = str(rawip)

    if ENABLE_DNSBL == 0:
        http_connect(rawip)
    else:
        contrue = 0
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
                    contrue = 0
                    break
            except dns.resolver.NXDOMAIN:
                contrue += 1
                continue

        if contrue == 5:
            http_connect(rawip)
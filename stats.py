import config
import datetime
import hashlib
import time
global config

def store_initial(host, nick, ident, time):
    m = hashlib.md5()
    m.update(host)
    m.update(nick)
    m.update(ident)
    m.update(str(time))
    uniquehash = m.hexdigest()
    if config.dbtype == "SQLite":
        config.curstats.execute("INSERT INTO tempstats (host, nick, ident, time, hash) VALUES (?, ?, ?, ?, ?)", (host, nick, ident, time, uniquehash))
    else:
        config.curstats.execute("INSERT INTO tempstats (host, nick, ident, time, hash) VALUES (%s, %s, %s, %s, %s)", (host, nick, ident, time, uniquehash))
        config.dbconnstats.commit()
    return uniquehash

def update_ip(ip, uhash):
    if config.dbtype == "SQLite":
        config.curstats.execute("UPDATE tempstats SET ip = ? WHERE hash = ?", (ip, uhash))
    else:
        config.curstats.execute("UPDATE tempstats SET ip = %s WHERE hash = %s", (ip, uhash))
        config.dbconnstats.commit()

def update_ban(typeban, port, socks, http_connect, dnsbl, uhash):
    print "%s %s %s %s %s %s" % (typeban, port, socks, http_connect, dnsbl, uhash)
    if config.dbtype == "SQLite":
        config.curstats.execute("INSERT INTO banstats SELECT * FROM tempstats WHERE hash = ?", [uhash])
        config.curstats.execute("DELETE FROM tempstats WHERE hash = ?", [uhash])
        if typeban == "dnsbl":
            config.curstats.execute("UPDATE banstats SET dnsbl = ? WHERE hash = ?", (dnsbl, uhash))
        elif typeban == "http":
            config.curstats.execute("UPDATE banstats SET port = ?, http_connect = ? WHERE hash = ?", (port, http_connect, uhash))
        elif typeban == "socks":
            config.curstats.execute("UPDATE banstats SET port = ?, socksv = ? WHERE hash = ?", (port, socks, uhash))
    else:
        config.curstats.execute("INSERT INTO banstats SELECT * FROM tempstats WHERE hash = %s", [uhash])
        config.curstats.execute("DELETE FROM tempstats WHERE hash = %s", [uhash])
        if typeban == "dnsbl":
            config.curstats.execute("UPDATE banstats SET dnsbl = %s WHERE hash = %s", (dnsbl, uhash))
        elif typeban == "http":
            config.curstats.execute("UPDATE banstats SET port = %s, http_connect = %s WHERE hash = %s", (port, http_connect, uhash))
        elif typeban == "socks":
            config.curstats.execute("UPDATE banstats SET port = %s, socksv = %s WHERE hash = %s", (port, socks, uhash))
        config.dbconnstats.commit()

def routine():
    epoch = int(time.time())
    if config.dbtype == "SQLite":
        config.curstats.execute("INSERT INTO connstats VALUES (?)", (epoch))
        config.curstats.execute("DELETE FROM tempstats WHERE ? - time >= 10", (epoch))
    else:
        config.curstats.execute("INSERT INTO connstats VALUES (%s)", [epoch])
        config.curstats.execute("DELETE FROM tempstats WHERE %s - time >= 10", [epoch])
    config.dbconnstats.commit()

def do_stats(target):
    config.cur.execute("SELECT COUNT(*) FROM connstats")
    value = config.cur.fetchone()
    config.cur.execute("SELECT COUNT(*) FROM banstats")
    banvalue = config.cur.fetchone()
    config.confproto.notice(target, "Scanned %s connections and detected %s threats." % (value[0], banvalue[0]))

def do_stats_depth(target, timein, pronoun, window, morestats, statsamnt):
    epoch = int(time.time())
    newvalue = epoch - int(timein)
    if config.dbtype == "SQLite":
        config.cur.execute("SELECT COUNT(*) FROM connstats WHERE ts >= ?", (newvalue))
        value = config.cur.fetchone()
        config.cur.execute("SELECT COUNT(*) FROM banstats WHERE time >= ?", (newvalue))
        banvalue = config.cur.fetchone()
        config.confproto.notice(target, "In the past %s %s, I have scanned %s clients and have detected %s threats." % (window, pronoun, value[0], banvalue[0]))
        if morestats:
            if statsamnt <= 0:
                statsamnt = 3
            config.cur.execute("SELECT * FROM banstats WHERE time >= ? ORDER BY time DESC LIMIT ?", (newvalue, statsamnt))
            config.confproto.notice(target, "Displaying last %s threats..." % (statsamnt))
            newint = 1
            for row in config.cur.fetchall():
                if row[8] != "NULL":
                    config.confproto.notice(target, "%d: %s, was banned on %s with ident %s appearing under blacklist %s. Their host was %s which resolved to %s." % (newint, row[3], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[9])), row[4], row[8], row[1], row[2]))
                elif row[6] != "NULL":
                    config.confproto.notice(target, "%d: %s, was banned on %s with ident %s. They were under socks%s on port %s. Their host was %s which resolved to %s." % (newint, row[3], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[9])), row[4], row[6], row[5], row[1], row[2]))
                elif row[7] != "NULL":
                    config.confproto.notice(target, "%d: %s, was banned on %s with ident %s. They were under a(n) %s http_connect proxy on port %s. Their host was %s which resolved to %s." % (newint, row[3], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[9])), row[4], row[7], row[5], row[1], row[2]))
                newint += 1
            config.confproto.notice(target, "End of threats.")
    else:
        config.cur.execute("SELECT COUNT(*) FROM connstats WHERE ts >= %s", [newvalue])
        value = config.cur.fetchone()
        config.cur.execute("SELECT COUNT(*) FROM banstats WHERE time >= %s", [newvalue])
        banvalue = config.cur.fetchone()
        config.confproto.notice(target, "In the past %s %s, I have scanned %s clients and have detected %s threats." % (window, pronoun, value[0], banvalue[0]))
        if morestats:
            if statsamnt <= 0:
                statsamnt = 3
            config.cur.execute("SELECT * FROM banstats WHERE time >= %s ORDER BY time DESC LIMIT %s", (newvalue, statsamnt))
            config.confproto.notice(target, "Displaying last %s threats..." % (statsamnt))
            newint = 1
            for row in config.cur.fetchall():
                if row[8] != "NULL":
                    config.confproto.notice(target, "%d: %s, was banned on %s with ident %s appearing under blacklist %s. Their host was %s which resolved to %s." % (newint, row[3], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[9])), row[4], row[8], row[1], row[2]))
                elif row[6] != "NULL":
                    config.confproto.notice(target, "%d: %s, was banned on %s with ident %s. They were under socks%s on port %s. Their host was %s which resolved to %s." % (newint, row[3], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[9])), row[4], row[6], row[5], row[1], row[2]))
                elif row[7] != "NULL":
                    config.confproto.notice(target, "%d: %s, was banned on %s with ident %s. They were under a(n) %s http_connect proxy on port %s. Their host was %s which resolved to %s." % (newint, row[3], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[9])), row[4], row[7], row[5], row[1], row[2]))
                newint += 1
            config.confproto.notice(target, "End of threats.")
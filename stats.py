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
	return uniquehash

def update_ip(ip, uhash):
	if config.dbtype == "SQLite":
		config.curstats.execute("UPDATE tempstats SET ip = ? WHERE hash = ?", (ip, uhash))
	else:
		config.curstats.execute("UPDATE tempstats SET ip = %s WHERE hash = %s", (ip, uhash))

def update_ban(typeban, port, socks, http_connect, dnsbl, uhash):
	if config.dbtype == "SQLite":
		config.curstats.execute("INSERT INTO banstats SELECT * FROM tempstats WHERE hash = ?", (uhash))
		config.curstats.execute("DELETE FROM tempstats WHERE hash = ?", (uhash))
		if typeban == "dnsbl":
			config.curstats.execute("UPDATE banstats SET dnsbl = ? WHERE hash = ?", (dnsbl, uhash))
		elif typeban == "http":
			config.curstats.execute("UPDATE banstats SET port = ?, http_connect = ? WHERE hash = ?", (port, http_connect, uhash))
		elif typeban == "socks":
			config.curstats.execute("UPDATE banstats SET port = ?, socksv = ? WHERE hash = ?", (port, socks, uhash))
	else:
		config.curstats.execute("INSERT INTO banstats SELECT * FROM tempstats WHERE hash = %s", (uhash))
		config.curstats.execute("DELETE FROM tempstats WHERE hash = %s", (uhash))
		if typeban == "dnsbl":
			config.curstats.execute("UPDATE banstats SET dnsbl = %s WHERE hash = %s", (dnsbl, uhash))
		elif typeban == "http":
			config.curstats.execute("UPDATE banstats SET port = %s, http_connect = %s WHERE hash = %s", (port, http_connect, uhash))
		elif typeban == "socks":
			config.curstats.execute("UPDATE banstats SET port = %s, socksv = %s WHERE hash = %s", (port, socks, uhash))

def routine():
	epoch = int(time.time())
	if config.dbtype == "SQLite":
		config.curstats.execute("DELETE FROM tempstats WHERE time - ? >= 10", (epoch))
		config.curstats.execute("INSERT INTO connstats VALUES (?)", (epoch))
	else:
		config.curstats.execute("DELETE FROM tempstats WHERE time - %s >= 10", (epoch))
		config.curstats.execute("INSERT INTO connstats VALUES (%s)", (epoch))

def do_stats(target):
	epoch = int(time.time())
	config.cur.execute("SELECT COUNT(*) FROM connstats")
	value = config.cur.fetchone()
	config.confproto.notice(target, "Scanned %s connections." % (value[0]))
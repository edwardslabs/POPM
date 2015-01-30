import random
from run import StartServer
import socket
import string
import sys
import time
import yaml
try:
    with open('config.yaml', 'r') as f:
        conf = yaml.load(f)
        NETWORK_NAME = conf["server"]["name"]
        HOST = conf["server"]["host"]
        PORT = conf["server"]["port"]
        SERVER_HOST_NAME = conf["server"]["self_server_host_name"]
        HOPS = conf["server"]["hops"]
        SERVER_DESCRIPTION = conf["server"]["server_description"]
        SERVER_NUMERIC = conf["server"]["server_numeric"]
        SERVER_PASS = conf["server"]["server_password"]
        BOT_NAME = conf["bot"]["nick"]
        BOT_HOST = conf["bot"]["host"]
        BOT_DESC = conf["bot"]["gecos"]
        BOT_MODE = conf["bot"]["umodes"]
        PREFIX = conf["bot"]["prefix"]
        DEBUG_CHANNEL = conf["bot"]["debug_channel"]
        DB_NAME = conf["database"]["dbname"]
        DB_USER = conf["database"]["user"]
        DB_HOST = conf["database"]["host"]
        DB_PASS = conf["database"]["pass"]
        DURATION = conf["misc"]["gline_duration"]
        SCAN_ON_BURST = conf["misc"]["scan_on_netburst"]
        PROTO = conf["server"]["protocol"]
        DNSBL_BAN_MSG = conf["proxy"]["dnsbl_ban_message"]
        HTTP_BAN_MSG = conf["proxy"]["http_ban_message"]
        SOCKS_BAN_MSG = conf["proxy"]["socks_ban_message"]
        DEBUG_LEVEL = conf["misc"]["debug_level"]
        SQL_ENGINE = conf["database"]["type"]

        # Config checker #
        if not isinstance(DURATION, int):
            sys.exit("[CONFIG ERROR]: misc:gline_duration must be an integer (in seconds)")

        if not isinstance(PORT, int):
            sys.exit("[CONFIG ERROR]: server:port must be an integer")

        if not isinstance(HOPS, int):
            sys.exit("[CONFIG ERROR]: server:hops must be an integer")

        if not len(SERVER_NUMERIC) == 2:
            sys.exit("[CONFIG ERROR]: server:server_numeric must be 2 letters/numers")

        if not isinstance(SCAN_ON_BURST, int):
            sys.exit("[CONFIG ERROR]: misc:scan_on_netburst must be either a 1 or 0 (true or false respectivly)")

        if SCAN_ON_BURST not in {0, 1}:
            sys.exit("[CONFIG ERROR]: misc:scan_on_netburst must be either a 1 or 0 (true or false respectivly)")

        if DEBUG_LEVEL not in range(0,7):
            sys.exit("[CONFIG ERROR]: misc:debug_level must be between 0 - 6. Consult the README for more information")

        if not DNSBL_BAN_MSG:
            DNSBL_BAN_MSG = "No reason given."

        if not HTTP_BAN_MSG:
            HTTP_BAN_MSG = "No reason given."

        if not SOCKS_BAN_MSG:
            SOCKS_BAN_MSG = "No reason given."

        if PROTO.lower() == "p10server":
            from p10server import P10Server
            confproto = P10Server()
        else:
            sys.exit("[CONFIG ERROR]: server:protocol must be P10Server (more support coming soon(tm))")

        if SQL_ENGINE.lower() == "mysql":
            dbtype = "MySQL"
            import MySQLdb
        elif SQL_ENGINE.lower() == "postgres":
            dbtype = "Postgres"
            import psycopg2
        elif SQL_ENGINE.lower() == "sqlite":
            dbtype = "SQLite"
            import sqlite3
        else:
            sys.exit("[CONFIG ERROR]: Invalid database type selected. Options: Postgres, MySQL, SQLite")

except IOError:
    sys.exit("[CONFIG ERROR]: config.yaml is missing!")

except KeyError:
    sys.exit("[CONFIG ERROR]: Your config file is incomplete; Please recopy config.yaml.example and rebase your settings from there.")

s=socket.socket()
validate=socket.socket()
main = StartServer()

def socketverify():
    try:
        validate.connect((HOST, PORT))
    except Exception, e:
        sys.exit("Error connecting to uplink server: %s" % (e))
    validate.close()

def dbverify():
    if dbtype == "Postgres":
        try:
            dbconn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
            cur = dbconn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS banstats (ID BIGSERIAL PRIMARY KEY, host TEXT NOT NULL, ip TEXT NOT NULL, nick TEXT NOT NULL, ident TEXT NOT NULL, port INT DEFAULT NULL, socksv INT DEFAULT NULL, http_connect TEXT DEFAULT NULL, dnsbl TEXT DEFAULT NULL, time INT NOT NULL, hash TEXT NOT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS tempstats (ID BIGSERIAL PRIMARY KEY, host TEXT NOT NULL, ip TEXT NOT NULL, nick TEXT NOT NULL, ident TEXT NOT NULL, port INT DEFAULT NULL, socksv INT DEFAULT NULL, http_connect TEXT DEFAULT NULL, dnsbl TEXT DEFAULT NULL, time INT NOT NULL, hash TEXT NOT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS connstats (ts INT NOT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS exemptions (ID BIGSERIAL PRIMARY KEY, ip TEXT NOT NULL, whenadded INT NOT NULL, whoadded TEXT NOT NULL, lastmodified INT DEFAULT NULL, expires INT, wholast TEXT DEFAULT NULL, perma BOOLEAN NOT NULL, reason TEXT, active BOOLEAN NOT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS settings (enable_dnsbl BOOLEAN NOT NULL, enable_http BOOLEAN NOT NULL, enable_socks BOOLEAN NOT NULL, access_die INT NOT NULL, access_set INT NOT NULL, access_say INT NOT NULL, access_emote INT NOT NULL, access_joinpart INT NOT NULL, view_exempts INT NOT NULL, modify_exempts INT NOT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS users (ID BIGSERIAL PRIMARY KEY, admin TEXT NOT NULL, added INT NOT NULL, access INT NOT NULL, bywho TEXT NOT NULL)")
            dbconn.commit()
            cur.execute("SELECT * FROM settings")
            if cur.rowcount == 0:
                cur.execute("INSERT INTO settings VALUES (True,True,True,1000,1000,1000,1000,1000,1000,1000)")
                dbconn.commit()
                print "Configuring settings..."
            else:
                cur.execute("SELECT * FROM settings WHERE access_die >= 0 AND access_die <= 1000 AND access_set >= 0 AND access_set <= 1000 AND access_say >= 0 AND access_say <= 1000 AND access_emote >= 0 AND access_emote <= 1000 AND access_joinpart >= 0 AND access_joinpart <= 1000 AND modify_exempts >= 0 AND modify_exempts <= 1000 AND enable_dnsbl = '1' OR enable_dnsbl = '0' AND enable_http = '1' OR enable_http = '0' AND enable_socks = '1' OR enable_socks = '0'")
                if cur.rowcount != 1:
                    sys.exit("Your database does not contain a valid `settings` table. Proxy monitors must either be set to on or off (Boolbean 0/1). Please check your database, or reimport the template .sql file.")
            cur.execute("SELECT admin FROM users")
            if cur.rowcount < 1:
                newkeypass = ''.join(random.choice(string.digits) for i in range(10))
                cur.execute("INSERT INTO users (admin, added, access, bywho) VALUES (%s, %s, 1000, 'POPM');", (newkeypass, int(time.time())))
                dbconn.commit()
                print "Welcome to POPM! Since there are no admins in my database, I have generated a new key for you to use."
                print "For starters, make sure you are authed with NickServ. Once you have that done, simply run this command:"
                print "/msg %s AUTHME %s" % (BOT_NAME, newkeypass)
                print "When you run this, you will be granted root priveleges for accessing settings in POPM via %s. If you" % (BOT_NAME)
                print "need any assistance, consult the README file found in POPM, or open up an issue on github at"
                print "https://github.com/blindirc/POPM Hope you enjoy using POPM!"
            elif cur.rowcount == 1:
                uid = cur.fetchone()
                try:
                    iuid = int(uid[0])
                    # If the username is an integer, then they haven't changed it. IRC rules, not mine. #
                    print "Welcome to POPM! You have an active activation request to claim root priveleges over POPM"
                    print "Please join the IRC network and /msg %s AUTHME %d" % (BOT_NAME, iuid)
                except ValueError:
                    # It's not a cookie we generated #
                    pass
            dbconn.close

            dbconnauto = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
            curauto = dbconnauto.cursor()
            dbconnauto.close()
        except psycopg2.OperationalError, v:
            sys.exit("A database error has occured: %s" % (v))
    elif dbtype == "MySQL":
        try:
            import warnings
            warnings.filterwarnings('ignore')
            # MySQL throws warnings for CREATE TABLE IF NOT EXISTS if the table exists... Why do we care exactly? Why would it throw a warning if it's doing what we tell it. #mysqllogic
            dbconn = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)
            cur = dbconn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS banstats (ID INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, host TEXT NOT NULL, ip TEXT NOT NULL, nick TEXT NOT NULL, ident TEXT NOT NULL, port INT(11) DEFAULT NULL, socksv INT(11) DEFAULT NULL, http_connect TEXT DEFAULT NULL, dnsbl TEXT DEFAULT NULL, time INT(11) NOT NULL, hash TEXT CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS tempstats (ID INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, host TEXT NOT NULL, ip TEXT NOT NULL, nick TEXT NOT NULL, ident TEXT NOT NULL, port INT(11) DEFAULT NULL, socksv INT(11) DEFAULT NULL, http_connect TEXT DEFAULT NULL, dnsbl TEXT DEFAULT NULL, time INT(11) NOT NULL, hash TEXT CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS connstats (ts INT(11) NOT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS exemptions (ID INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, ip TEXT NOT NULL, whenadded INT(11) NOT NULL, whoadded TEXT NOT NULL, lastmodified INT(11) DEFAULT NULL, expires INT(11), wholast TEXT DEFAULT NULL, perma BOOLEAN NOT NULL, reason TEXT, active BOOLEAN NOT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS settings (enable_dnsbl BOOLEAN NOT NULL, enable_http BOOLEAN NOT NULL, enable_socks BOOLEAN NOT NULL, access_die INT(11) NOT NULL, access_set INT(11) NOT NULL, access_say INT(11) NOT NULL, access_emote INT(11) NOT NULL, access_joinpart INT(11) NOT NULL, view_exempts INT(11) NOT NULL, modify_exempts INT(11) NOT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS users (ID INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, admin TEXT NOT NULL, added INT(11) NOT NULL, access INT(11) NOT NULL, bywho TEXT NOT NULL)")
            cur.execute("SELECT * FROM settings WHERE access_die >= 0 AND access_die <= 1000 AND access_set >= 0 AND access_set <= 1000 AND access_say >= 0 AND access_say <= 1000 AND access_emote >= 0 AND access_emote <= 1000 AND access_joinpart >= 0 AND access_joinpart <= 1000 AND modify_exempts >= 0 AND modify_exempts <= 1000")
            if cur.rowcount == 0:
                cur.execute("INSERT INTO settings VALUES (1,1,1,1000,1000,1000,1000,1000,1000,1000)")
                dbconn.commit()
                print "Configuring settings..."
            else:
                cur.execute("SELECT * FROM settings WHERE enable_dnsbl = '1' OR enable_dnsbl = '0' AND enable_http = '1' OR enable_http = '0' AND enable_socks = '1' OR enable_socks = '0'")
                if cur.rowcount != 1:
                    sys.exit("Your database does not contain a valid `settings` table. Proxy monitors must either be set to on or off (Boolbean 0/1). Please check your database, or reimport the template .sql file.")
            cur.execute("SELECT admin FROM users")
            if cur.rowcount < 1:
                newkeypass = ''.join(random.choice(string.digits) for i in range(10))
                cur.execute("INSERT INTO users (admin, added, access, bywho) VALUES (%s, %s, 1000, 'POPM');", (newkeypass, int(time.time())))
                dbconn.commit()
                print "Welcome to POPM! Since there are no admins in my database, I have generated a new key for you to use."
                print "For starters, make sure you are authed with NickServ. Once you have that done, simply run this command:"
                print "/msg %s AUTHME %s" % (BOT_NAME, newkeypass)
                print "When you run this, you will be granted root priveleges for accessing settings in POPM via %s. If you" % (BOT_NAME)
                print "need any assistance, consult the README file found in POPM, or open up an issue on github at"
                print "https://github.com/blindirc/POPM Hope you enjoy using POPM!"
            elif cur.rowcount == 1:
                uid = cur.fetchone()
                try:
                    iuid = int(uid[0])
                    # If the username is an integer, then they haven't changed it. IRC rules, not mine. #
                    print "Welcome to POPM! You have an active activation request to claim root priveleges over POPM"
                    print "Please join the IRC network and /msg %s AUTHME %d" % (BOT_NAME, iuid)
                except ValueError:
                    # It's not a cookie we generated #
                    pass
            dbconn.close()

            dbconnauto = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)
            curauto = dbconnauto.cursor()
            dbconnauto.close()
        except MySQLdb.OperationalError, v:
            sys.exit("A database error has occured: %s" % (v))
    elif dbtype == "SQLite":
        dbconn = sqlite3.connect('popm.db', isolation_level=None)
        cur = dbconn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS exemptions (ID INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT NOT NULL, whenadded INT NOT NULL, whoadded TEXT NOT NULL, lastmodified INT DEFAULT NULL, expires INT NOT NULL, wholast TEXT DEFAULT NULL, perma BOOLEAN, reason TEXT, active BOOLEAN)")
        cur.execute("CREATE TABLE IF NOT EXISTS users (ID INTEGER PRIMARY KEY AUTOINCREMENT, admin TEXT NOT NULL, added INT NOT NULL, access INT NOT NULL, bywho TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS settings (enable_dnsbl BOOLEAN NOT NULL, enable_http BOOLEAN NOT NULL, enable_socks BOOLEAN NOT NULL, access_die INT(11), access_set INT(11), access_say INT(11), access_emote INT(11), access_joinpart INT(11), view_exempts INT(11), modify_exempts INT(11))")
        cur.execute("CREATE TABLE IF NOT EXISTS banstats (UID INTEGER PRIMARY KEY AUTOINCREMENT, host TEXT NOT NULL, ip TEXT DEFAULT NULL, nick TEXT NOT NULL, ident TEXT NOT NULL, port INT(11) DEFAULT NULL, socksv INT(11) DEFAULT NULL, http_connect TEXT DEFAULT NULL, dnsbl TEXT DEFAULT NULL, time INT(11) NOT NULL, hash TEXT NOT NULL)")
        cur.execute("CREATE TABLE IF NOT EXISTS tempstats (UID INTEGER PRIMARY KEY AUTOINCREMENT, host TEXT NOT NULL, ip TEXT DEFAULT NULL, nick TEXT NOT NULL, ident TEXT NOT NULL, port INT(11) DEFAULT NULL, socksv INT(11) DEFAULT NULL, http_connect TEXT DEFAULT NULL, dnsbl TEXT DEFAULT NULL, time INT(11) NOT NULL, hash TEXT NOT NULL)")
        cur.execute("CREATE TABLE IF NOT EXISTS connstats (ts INTEGER)")
        cur.execute("SELECT COUNT(*) FROM settings")
        value = cur.fetchone()
        if value[0] == 0:
            cur.execute("INSERT INTO settings (enable_dnsbl,enable_http,enable_socks,access_die,access_set,access_say,access_emote,access_joinpart,view_exempts,modify_exempts) VALUES ('1', '1', '1', 1000, 1000, 1000, 1000, 1000, 1000, 1000)")
            print "Initializing settings..."
        cur.execute("SELECT COUNT(*) FROM users")
        items = cur.fetchone()
        if items[0] < 1:
            newkeypass = ''.join(random.choice(string.digits) for i in range(10))
            cur.execute("INSERT INTO users (admin, added, access, bywho) VALUES (?, ?, 1000, 'POPM')", (newkeypass, int(time.time())))
            dbconn.commit()
            print "Welcome to POPM! Since there are no admins in my database, I have generated a new key for you to use."
            print "For starters, make sure you are authed with NickServ. Once you have that done, simply run this command:"
            print "/msg %s AUTHME %s" % (BOT_NAME, newkeypass)
            print "When you run this, you will be granted root priveleges for accessing settings in POPM via %s. If you" % (BOT_NAME)
            print "need any assistance, consult the README file found in POPM, or open up an issue on github at"
            print "https://github.com/blindirc/POPM Hope you enjoy using POPM!"
        elif items[0] == 1:
            cur.execute("SELECT admin FROM users")
            uid = cur.fetchone()
            try:
                iuid = int(uid[0])
                # If the username is an integer, then they haven't changed it. IRC rules, not mine. #
                print "Welcome to POPM! You have an active activation request to claim root priveleges over POPM"
                print "Please join the IRC network and /msg %s AUTHME %d" % (BOT_NAME, iuid)
            except ValueError:
                pass
def dbconnect():
    # Cursor for user commands
    global dbconn
    global cur

    # Cursor for automatic POPM configurations
    global dbconnauto
    global curauto

    # Stats command so it doesn't trip over auto
    global dbconnstats
    global curstats

    if dbtype == "Postgres":
        dbconn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
        cur = dbconn.cursor()
        dbconnauto = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
        curauto = dbconnauto.cursor()
        dbconnstats = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
        curstats = dbconnstats.cursor()

    elif dbtype == "MySQL":
        dbconn = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)
        dbconn.autocommit(True)
        cur = dbconn.cursor()

        dbconnauto = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)
        dbconnauto.autocommit(True)
        curauto = dbconnauto.cursor()

        dbconnstats = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)
        dbconnstats.autocommit(True)
        curstats = dbconnstats.cursor()

    elif dbtype == "SQLite":
        dbconn = sqlite3.connect('popm.db', isolation_level=None)
        cur = dbconn.cursor()
        dbconnauto = sqlite3.connect('popm.db', isolation_level=None)
        curauto = dbconn.cursor()
        dbconnstats = sqlite3.connect('popm.db', isolation_level=None)
        curstats = dbconnstats.cursor()
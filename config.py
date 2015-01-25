from run import StartServer
import socket
import sys
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
        else:
            sys.exit("[CONFIG ERROR]: Invalid database type selected. Options: Postgres, MySQL")

except IOError:
    print "[CONFIG ERROR]: config.yaml is missing!"
    sys.exit()
except KeyError:
    print "[CONFIG ERROR]: Your config file is incomplete; Please recopy config.yaml.example and rebase your settings from there."
    sys.exit()

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
            cur.execute("SELECT * FROM settings WHERE access_die >= 0 AND access_die <= 1000 AND access_set >= 0 AND access_set <= 1000 AND access_say >= 0 AND access_say <= 1000 AND access_emote >= 0 AND access_emote <= 1000 AND access_joinpart >= 0 AND access_joinpart <= 1000 AND modify_exempts >= 0 AND modify_exempts <= 1000")
            if cur.rowcount != 1:
                sys.exit("Your PostgreSQL database does not contain a valid `settings` table. The access roles must be between 0 - 1000. Please check your database, or reimport the template .sql file.")
            cur.execute("SELECT * FROM settings WHERE enable_dnsbl = '1' OR enable_dnsbl = '0' AND enable_http = '1' OR enable_http = '0' AND enable_socks = '1' OR enable_socks = '0'")
            if cur.rowcount != 1:
                sys.exit("Your PostgreSQL database does not contain a valid `settings` table. Proxy monitors must either be set to on or off (Boolbean 0/1). Please check your database, or reimport the template .sql file.")
            cur.execute("SELECT * FROM users")
            if cur.rowcount < 1:
                print "WARNING: POPM does not have a list of admins. It is reccomended to add yourself to the `users` table in PostgreSQL to gain admin priveleges. There will be a startup admin cookie generated in the future to prevent this."
            dbconn.close()

            dbconnauto = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
            curauto = dbconnauto.cursor()
            dbconnauto.close()
        except psycopg2.OperationalError, v:
            sys.exit("A database error has occured: %s" % (v))
    elif dbtype == "MySQL":
        try:
            dbconn = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)
            cur = dbconn.cursor()
            cur.execute("SELECT * FROM settings WHERE access_die >= 0 AND access_die <= 1000 AND access_set >= 0 AND access_set <= 1000 AND access_say >= 0 AND access_say <= 1000 AND access_emote >= 0 AND access_emote <= 1000 AND access_joinpart >= 0 AND access_joinpart <= 1000 AND modify_exempts >= 0 AND modify_exempts <= 1000")
            if cur.rowcount != 1:
                sys.exit("Your database does not contain a valid `settings` table. The access roles must be between 0 - 1000. Please check your database, or reimport the template .sql file.")
            cur.execute("SELECT * FROM settings WHERE enable_dnsbl = '1' OR enable_dnsbl = '0' AND enable_http = '1' OR enable_http = '0' AND enable_socks = '1' OR enable_socks = '0'")
            if cur.rowcount != 1:
                sys.exit("Your database does not contain a valid `settings` table. Proxy monitors must either be set to on or off (Boolbean 0/1). Please check your database, or reimport the template .sql file.")
            cur.execute("SELECT * FROM users")
            if cur.rowcount < 1:
                print "WARNING: POPM does not have a list of admins. It is recommended to add yourself to the `users` table in the database to gain admin priveleges. There will be a startup admin cookie generated in the future to prevent this."
            dbconn.close()

            dbconnauto = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)
            curauto = dbconnauto.cursor()
            dbconnauto.close()
        except MySQLdb.OperationalError, v:
            sys.exit("A database error has occured: %s" % (v))

def dbconnect():
    global dbconn
    global cur
    global dbconnauto
    global curauto
    if dbtype == "Postgres":
        dbconn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
        cur = dbconn.cursor()
        dbconnauto = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
        curauto = dbconnauto.cursor()
    elif dbtype == "MySQL":
        dbconn = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)
        dbconn.autocommit(True)
        cur = dbconn.cursor()
        dbconnauto = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)
        dbconnauto.autocommit(True)
        curauto = dbconnauto.cursor()
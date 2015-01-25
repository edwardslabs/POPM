from bot import StartServer
import psycopg2
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

        # Config checker #
        if not isinstance(DURATION, int):
            print "[CONFIG ERROR]: misc:gline_duration must be an integer (in seconds)"
            sys.exit()

        if not isinstance(PORT, int):
            print "[CONFIG ERROR]: server:port must be an integer"
            sys.exit()

        if not isinstance(HOPS, int):
            print "[CONFIG ERROR]: server:hops must be an integer"
            sys.exit()

        if not len(SERVER_NUMERIC) == 2:
            print "[CONFIG ERROR]: server:server_numeric must be 2 letters/numers"
            sys.exit()

        if not isinstance(SCAN_ON_BURST, int):
            print "[CONFIG ERROR]: misc:scan_on_netburst must be either a 1 or 0 (true or false respectivly)"
            sys.exit()

        if SCAN_ON_BURST not in {0, 1}:
            print "[CONFIG ERROR]: misc:scan_on_netburst must be either a 1 or 0 (true or false respectivly)"
            sys.exit()

        if DEBUG_LEVEL not in range(0,7):
            print "[CONFIG ERROR]: misc:debug_level must be between 0 - 6. Consult the README for more information"
            sys.exit()

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
            print "[CONFIG ERROR]: server:protocol must be P10Server (more support coming soon(tm))"
            sys.exit()

except IOError:
    print "[CONFIG ERROR]: config.yaml is missing!"
    sys.exit()
except KeyError:
    print "[CONFIG ERROR]: Your config file is incomplete; Please recopy config.yaml.example and rebase your settings from there."
    sys.exit()

s=socket.socket()
main = StartServer()

def dbverify():
    try:
        pgconn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
        cur = pgconn.cursor()
        cur.execute("SELECT * FROM settings WHERE access_die >= 0 AND access_die <= 1000 AND access_set >= 0 AND access_set <= 1000 AND access_say >= 0 AND access_say <= 1000 AND access_emote >= 0 AND access_emote <= 1000 AND access_joinpart >= 0 AND access_joinpart <= 1000 AND modify_exempts >= 0 AND modify_exempts <= 1000")
        if cur.rowcount != 1:
            sys.exit("Your PostgreSQL database does not contain a valid `settings` table. The access roles must be between 0 - 1000. Please check your database, or reimport the template .sql file.")
        cur.execute("SELECT * FROM settings WHERE enable_dnsbl = '1' OR enable_dnsbl = '0' AND enable_http = '1' OR enable_http = '0' AND enable_socks = '1' OR enable_socks = '0'")
        if cur.rowcount != 1:
            sys.exit("Your PostgreSQL database does not contain a valid `settings` table. Proxy monitors must either be set to on or off (Boolbean 0/1). Please check your database, or reimport the template .sql file.")
        cur.execute("SELECT * FROM users")
        if cur.rowcount < 1:
            print "WARNING: POPM does not have a list of admins. It is reccomended to add yourself to the `users` table in PostgreSQL to gain admin priveleges. There will be a startup admin cookie generated in the future to prevent this."
        pgconn.close()

        pgconnauto = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
        curauto = pgconnauto.cursor()
        pgconnauto.close()
    except psycopg2.OperationalError, v:
        sys.exit("A database error has occured: %s" % (v))

def dbconnect():
    global cur
    global pgconn
    global pgconnauto
    global curauto

    pgconn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
    cur = pgconn.cursor()
    # Have cursor dedicated for settings look ups #
    pgconnauto = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
    curauto = pgconnauto.cursor()
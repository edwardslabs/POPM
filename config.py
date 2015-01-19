import yaml
import sys
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

        # Config checker #
        if not isinstance( DURATION, int ):
            print "[CONFIG ERROR]: misc:gline_duration must be an integer (in seconds)"
            sys.exit()
        if not isinstance( PORT, int ):
            print "[CONFIG ERROR]: server:port must be an integer"
            sys.exit()
        if not isinstance( HOPS, int ):
            print "[CONFIG ERROR]: server:hops must be an integer"
            sys.exit()
        if not len(SERVER_NUMERIC) == 2:
            print "[CONFIG ERROR]: server:server_numeric must be 2 letters/numers"
        if not isinstance( SCAN_ON_BURST, int ):
            print "[CONFIG ERROR]: misc:scan_on_netburst must be either a 1 or 0 (true or false respectivly)"
            sys.exit()
        if not SCAN_ON_BURST == 0 or SCAN_ON_BURST == 1:
            print "[CONFIG ERROR]: misc:scan_on_netburst must be either a 1 or 0 (true or false respectivly)"
            sys.exit()

except IOError:
    print "[CONFIG ERROR]: config.yaml is missing!"
    sys.exit()
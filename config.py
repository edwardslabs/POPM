class Config:
    def __init__(self):
        import yaml
        import __builtin__
        with open('config.yaml', 'r') as f:
            conf = yaml.load(f)
            self.NETWORK_NAME = conf["server"]["name"]
            self.HOST = conf["server"]["host"]
            self.PORT = conf["server"]["port"]
            self.SERVER_HOST_NAME = conf["server"]["self_server_host_name"]
            self.HOPS = conf["server"]["hops"]
            self.SERVER_DESCRIPTION = conf["server"]["server_description"]
            self.SERVER_NUMERIC = conf["server"]["server_numeric"]
            self.SERVER_PASS = conf["server"]["server_password"]
            self.BOT_NAME = conf["bot"]["nick"]
            self.BOT_HOST = conf["bot"]["host"]
            self.BOT_DESC = conf["bot"]["gecos"]
            self.BOT_MODE = conf["bot"]["umodes"]
            self.DEBUG_CHANNEL = conf["bot"]["debug_channel"]
            self.DB_NAME = conf["database"]["dbname"]
            self.DB_USER = conf["database"]["user"]
            self.DB_HOST = conf["database"]["host"]
            self.DB_PASS = conf["database"]["pass"]
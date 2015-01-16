class Database:
    def __init__(self):
    	import config
    	import psycopg2
    	cfg = config.Config()
        self.pgconn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (cfg.DB_NAME, cfg.DB_USER, cfg.DB_HOST, cfg.DB_PASS))
        self.cur = self.pgconn.cursor()
        # Have cursor dedicated for settings look ups #
        self.pgconnauto = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (cfg.DB_NAME, cfg.DB_USER, cfg.DB_HOST, cfg.DB_PASS))
        self.curauto = self.pgconnauto.cursor()
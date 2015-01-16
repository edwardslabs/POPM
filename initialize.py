class Initialize:
    def main(self):
    	import database
    	import server
    	serv = server.Server()
    	db = database.Database()
        db.curauto.execute("SELECT enable_dnsbl,enable_http,enable_socks,access_die,access_set FROM settings")
        for row in db.curauto.fetchall():
            ENABLE_DNSBL = row[0]
            ENABLE_HTTP = row[1]
            ENABLE_SOCKS = row[2]
            ACCESS_DIE = row[3]
            ACCESS_SET = row[4]

        serv.main()
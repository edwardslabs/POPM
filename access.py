class UserAccess:
    '''
    Handle data from getting user information
    '''
    import config
    cfg = config.Config()
    HOST = cfg.HOST
    PORT = cfg.PORT
    SERVER_PASS = cfg.SERVER_PASS
    SERVER_HOST_NAME = cfg.SERVER_HOST_NAME
    HOPS = cfg.HOPS
    SERVER_NUMERIC = cfg.SERVER_NUMERIC
    SERVER_DESCRIPTION = cfg.SERVER_DESCRIPTION
    BOT_NAME = cfg.BOT_NAME
    BOT_HOST = cfg.BOT_HOST
    BOT_MODE = cfg.BOT_MODE
    BOT_DESC = cfg.BOT_DESC
    DEBUG_CHANNEL = cfg.DEBUG_CHANNEL
    def show_access(self, target, source):
        import server
        import config
        import database
        DB = database.Database()
        config = config.Config()
        conn = server.Server()
        if target == "*":
            DB.cur.execute("SELECT access,admin FROM users")
            s.send("%sAAA O %s :Account    Level\n" % (SERVER_NUMERIC, source))
            num = 0
            for row in DB.cur.fetchall():
                s.send("%sAAA O %s :%s  %s\n" % (SERVER_NUMERIC, source, row[1], row[0]))
                num += 1
            s.send("%sAAA O %s :Found %d matches.\n" % (SERVER_NUMERIC, source, num))
        else:
            DB.cur.execute("SELECT access,admin FROM users WHERE admin = %r" % (target))
            if DB.cur.rowcount < 1:
                s.send("%sAAA O %s :Could not find account %s.\n" % (SERVER_NUMERIC, source, target))
            else:
                for row in DB.cur.fetchall():
                    account = row[1]
                    access = row[0]
                s.send("%sAAA O %s :Account %s has access %d.\n" % (SERVER_NUMERIC, source, account, access))

    def get_level_req(self, param):
        import database
        DB = database.Database()
        if param == "access_set":
            DB.cur.execute("SELECT access_set FROM settings")
            level = 0
            for row in DB.cur.fetchall():
                level = row[0]
            return level
        elif param == "setters":
            DB.cur.execute("SELECT access_set FROM settings")
            level = 0
            for row in DB.cur.fetchall():
                level = row[0]
            return level

    def update_access(self, user, level, whodidit, userlist):
        import server
        import config
        import database
        DB = database.Database()
        config = config.Config()
        conn = server.Server()
        if isinstance(level, int):
            bywho = get_acc(whodidit)
            DB.cur.execute("SELECT admin FROM users WHERE admin = %r" % (user))
            epoch = int(time.time())
            if DB.cur.rowcount < 1:
                if level < 0:
                    s.send("%sAAA O %s :Account %s does not exist.\n" % (SERVER_NUMERIC, whodidit, user))
                else:
                    DB.cur.execute("INSERT INTO users (admin,access,added,bywho) VALUES (%r, %r, %r, %r)" % (user, level, epoch, bywho))
                    pgconn.commit()
                    s.send("%sAAA O %s :Account %s has been added with access %d.\n" % (SERVER_NUMERIC, whodidit, user, level))
            else:
                if level < 0:
                    DB.cur.execute("DELETE FROM users * WHERE admin = %r" % (user))
                    pgconn.commit()
                    s.send("%sAAA O %s :Access for account %s has been deleted.\n" % (SERVER_NUMERIC, whodidit, user))
                else:
                    DB.cur.execute("UPDATE users SET access = %r, bywho = %r, added = %r WHERE admin = %r" % (level, bywho, epoch, user))
                    pgconn.commit()
                    s.send("%sAAA O %s :Account %s has been updated to access %d.\n" % (SERVER_NUMERIC, whodidit, user, level))
        else:
            s.send("%sAAA O %s :Access levels must be an integer.\n" % (SERVER_NUMERIC, whodidit))

    def get_acc(self, numnick, userlist):
        authed = 0
        access = 0
        for i in userlist:
            account = i.split(":")[0]
            ircnum = i.split(":")[1]
            if ircnum == numnick:
                return account

    def access_level(self, numnick, userlist):
        import server
        import config
        import database
        DB = database.Database()
        config = config.Config()
        conn = server.Server()
        authed = 0
        access = 0
        for i in userlist:
            account = i.split(":")[0]
            ircnum = i.split(":")[1]
            if ircnum == numnick:
                authed += 1
        if authed == 0:
            conn.s.send("%sAAA O %s :You must first authenticate with NickServ.\n" % (config.SERVER_NUMERIC, numnick))
        else:
            DB.cur.execute("SELECT access FROM users WHERE admin = %r" % (account))
            is_user = 0
            for row in DB.cur.fetchall():
                access = row[0]
                is_user += 1
            if is_user > 0:
                return access
            else:
                conn.s.send("%sAAA O %s :You must first authenticate with NickServ.\n" % (config.SERVER_NUMERIC, numnick))
                return False
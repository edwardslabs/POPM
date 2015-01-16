def show_access(target, source):
    from config import *
    from bot import *
    from server import *
    if target == "*":
        cur.execute("SELECT access,admin FROM users")
        s.send("%sAAA O %s :Account    Level\n" % (SERVER_NUMERIC, source))
        num = 0
        for row in cur.fetchall():
            s.send("%sAAA O %s :%s  %s\n" % (SERVER_NUMERIC, source, row[1], row[0]))
            num += 1
        s.send("%sAAA O %s :Found %d matches.\n" % (SERVER_NUMERIC, source, num))
    else:
        cur.execute("SELECT access,admin FROM users WHERE admin = %r" % (target))
        if cur.rowcount < 1:
            s.send("%sAAA O %s :Could not find account %s.\n" % (SERVER_NUMERIC, source, target))
        else:
            for row in cur.fetchall():
                account = row[1]
                access = row[0]
            s.send("%sAAA O %s :Account %s has access %d.\n" % (SERVER_NUMERIC, source, account, access))

def get_level_req(param):
    from config import *
    from bot import *
    if param == "access_set":
        cur.execute("SELECT access_set FROM settings")
        level = 0
        for row in cur.fetchall():
            level = row[0]
        return level
    elif param == "setters":
        cur.execute("SELECT access_set FROM settings")
        level = 0
        for row in cur.fetchall():
            level = row[0]
        return level

def update_access(user, level, whodidit, userlist):
    from config import *
    from server import *
    from bot import *
    if isinstance(level, int):
        bywho = get_acc(whodidit, userlist)
        cur.execute("SELECT admin FROM users WHERE admin = %r" % (user))
        epoch = int(time.time())
        if cur.rowcount < 1:
            if level < 0:
                s.send("%sAAA O %s :Account %s does not exist.\n" % (SERVER_NUMERIC, whodidit, user))
            else:
                cur.execute("INSERT INTO users (admin,access,added,bywho) VALUES (%r, %r, %r, %r)" % (user, level, epoch, bywho))
                pgconn.commit()
                s.send("%sAAA O %s :Account %s has been added with access %d.\n" % (SERVER_NUMERIC, whodidit, user, level))
        else:
            if level < 0:
                cur.execute("DELETE FROM users * WHERE admin = %r" % (user))
                pgconn.commit()
                s.send("%sAAA O %s :Access for account %s has been deleted.\n" % (SERVER_NUMERIC, whodidit, user))
            else:
                cur.execute("UPDATE users SET access = %r, bywho = %r, added = %r WHERE admin = %r" % (level, bywho, epoch, user))
                pgconn.commit()
                s.send("%sAAA O %s :Account %s has been updated to access %d.\n" % (SERVER_NUMERIC, whodidit, user, level))
    else:
        s.send("%sAAA O %s :Access levels must be an integer.\n" % (SERVER_NUMERIC, whodidit))

def get_acc(numnick, userlist):
    authed = 0
    access = 0
    for i in userlist:
        account = i.split(":")[0]
        ircnum = i.split(":")[1]
        if ircnum == numnick:
            return account

def access_level(numnick, userlist):
    from config import *
    from server import *
    from bot import *
    authed = 0
    access = 0
    for i in userlist:
        account = i.split(":")[0]
        ircnum = i.split(":")[1]
        if ircnum == numnick:
            authed += 1
    if authed == 0:
        s.send("%sAAA O %s :You must first authenticate with NickServ.\n" % (SERVER_NUMERIC, numnick))
    else:
        cur.execute("SELECT access FROM users WHERE admin = %r" % (account))
        is_user = 0
        for row in cur.fetchall():
            access = row[0]
            is_user += 1
        if is_user > 0:
            return access
        else:
            s.send("%sAAA O %s :You must first authenticate with NickServ.\n" % (SERVER_NUMERIC, numnick))
            return False
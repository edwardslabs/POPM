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
        esctarget = "'" + str(target) + "'"
        cur.execute("SELECT access,admin FROM users WHERE admin = %s" % (esctarget))
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
        escuser = "'" + str(user) + "'"
        cur.execute("SELECT admin FROM users WHERE admin = %s" % (escuser))
        epoch = int(time.time())
        if cur.rowcount < 1:
            if level < 0:
                s.send("%sAAA O %s :Account %s does not exist.\n" % (SERVER_NUMERIC, whodidit, user))
            else:
                esclevel = "'" + str(level) + "'"
                escbywho = "'" + str(bywho) + "'"
                escepoch = "'" + str(epoch) + "'"
                esuser = "'" + str(user) + "'"
                cur.execute("INSERT INTO users (admin,access,added,bywho) VALUES (%s, %s, %s, %s)" % (esuser, esclevel, escepoch, escbywho))
                pgconn.commit()
                s.send("%sAAA O %s :Account %s has been added with access %d.\n" % (SERVER_NUMERIC, whodidit, user, level))
        else:
            if level < 0:
                escuser = "'" + str(user) + "'"
                cur.execute("DELETE FROM users * WHERE admin = %s" % (escuser))
                pgconn.commit()
                s.send("%sAAA O %s :Access for account %s has been deleted.\n" % (SERVER_NUMERIC, whodidit, user))
            else:
                esclevel = "'" + str(level) + "'"
                escbywho = "'" + str(bywho) + "'"
                escepoch = "'" + str(epoch) + "'"
                esuser = "'" + str(user) + "'"
                cur.execute("UPDATE users SET access = %s, bywho = %s, added = %s WHERE admin = %s" % (esclevel, escbywho, escepoch, esuser))
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
        escaccount = "'" + str(account) + "'"
        cur.execute("SELECT access FROM users WHERE admin = %s" % (escaccount))
        is_user = 0
        for row in cur.fetchall():
            access = row[0]
            is_user += 1
        if is_user > 0:
            return access
        else:
            s.send("%sAAA O %s :You must first authenticate with NickServ.\n" % (SERVER_NUMERIC, numnick))
            return False
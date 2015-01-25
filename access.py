import config
global config

def show_access(target, source):
    if target == "*":
        config.cur.execute("SELECT access,admin FROM users")
        config.confproto.notice(source, "Account    Level")
        num = 0
        for row in config.cur.fetchall():
            config.confproto.notice(source, "%s  %s" % (row[1], row[0]))
            num += 1
        config.confproto.notice(source, "Found %d matches." % (num))
    else:
        esctarget = "'" + str(target) + "'"
        config.cur.execute("SELECT access,admin FROM users WHERE admin = %s", [esctarget])
        if config.cur.rowcount < 1:
            config.confproto.notice(source, "Could not find account %s." % (target))
        else:
            for row in config.cur.fetchall():
                account = row[1]
                access = row[0]
            config.confproto.notice(source, "Account %s has access %d." % (account, access))

def get_level_req(param):
    if param == "access_set":
        config.cur.execute("SELECT access_set FROM settings")
        level = config.cur.fetchone()
        return level[0]
    elif param == "setters":
        config.cur.execute("SELECT access_set FROM settings")
        level = config.cur.fetchone()
        return level[0]

def update_access(user, level, whodidit, userlist):
    import time
    if isinstance(level, int):
        bywho = get_acc(whodidit, userlist)
        config.cur.execute("SELECT admin FROM users WHERE admin = %s", [user])
        epoch = int(time.time())
        if config.cur.rowcount < 1:
            if level < 0:
                config.confproto.notice(whodidit, "Account %s does not exist." % (user))
            else:
                config.cur.execute("INSERT INTO users (admin,access,added,bywho) VALUES (%s, %s, %s, %s)", (user, level, epoch, bywho))
                config.dbconn.commit()
                config.confproto.notice(whodidit, "Account %s has been added with access %d." % (user, level))
        else:
            if level < 0:
                config.cur.execute("DELETE FROM users WHERE admin = %s", [user])
                config.dbconn.commit()
                config.confproto.notice(whodidit, "Access for account %s has been deleted." % (user))
            else:
                config.cur.execute("UPDATE users SET access = %s, bywho = %s, added = %s WHERE admin = %s", (level, bywho, epoch, user))
                config.dbconn.commit()
                config.confproto.notice(whodidit, "Account %s has been updated to access %d." % (user, level))
    else:
        config.confproto.notice(whodidit, "Access levels must be an integer.")

def is_authed(numnick, userlist):
    authed = 0
    for i in userlist:
        account = i.split(":")[0]
        ircnum = i.split(":")[1]
        if ircnum == numnick:
            authed += 1
    if authed == 0:
        return False
    else:
        return True

def get_acc(numnick, userlist):
    for i in userlist:
        account = i.split(":")[0]
        ircnum = i.split(":")[1]
        if ircnum == numnick:
            return account

def access_level(numnick, userlist):
    authed = 0
    access = 0
    for i in userlist:
        if numnick == i.split(":")[1]:
            account = i.split(":")[0]
            ircnum = i.split(":")[1]
            authed += 1
            break
    if authed == 0:
        return False
    else:
        config.cur.execute("SELECT access FROM users WHERE admin = %s", [account])
        access = config.cur.fetchone()
        if access is not None:
            return access[0]
        else:
            return False

def my_access(numnick, userlist):
    authed = 0
    access = 0
    for i in userlist:
        if numnick == i.split(":")[1]:
            account = i.split(":")[0]
            ircnum = i.split(":")[1]
            authed += 1
            break
    if authed == 0:
        config.confproto.notice(numnick, "You must first authenticate with NickServ.")
    else:
        config.cur.execute("SELECT access FROM users WHERE admin = %s", [account])
        access = config.cur.fetchone()
        if access is not None:
            return access[0]
        else:
            config.confproto.notice(numnick, "You must first authenticate with NickServ.")
            return False
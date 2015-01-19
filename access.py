def show_access(target, source):
    from config import *
    from bot import *
    from commands import serv_notice
    if target == "*":
        cur.execute("SELECT access,admin FROM users")
        serv_notice(source, "Account    Level")
        num = 0
        for row in cur.fetchall():
            serv_notice(source, "%s  %s" % (row[1], row[0]))
            num += 1
        serv_notice(source, "Found %d matches." % (num))
    else:
        esctarget = "'" + str(target) + "'"
        cur.execute("SELECT access,admin FROM users WHERE admin = %s", [esctarget])
        if cur.rowcount < 1:
            serv_notice(source, "Could not find account %s." % (target))
        else:
            for row in cur.fetchall():
                account = row[1]
                access = row[0]
            serv_notice(source, "Account %s has access %d." % (account, access))

def get_level_req(param):
    from config import *
    from bot import *
    if param == "access_set":
        cur.execute("SELECT access_set FROM settings")
        level = cur.fetchone()
        return level[0]
    elif param == "setters":
        cur.execute("SELECT access_set FROM settings")
        level = cur.fetchone()
        return level[0]

def update_access(user, level, whodidit, userlist):
    from config import *
    from bot import *
    from commands import serv_notice
    if isinstance(level, int):
        bywho = get_acc(whodidit, userlist)
        cur.execute("SELECT admin FROM users WHERE admin = %s", [user])
        epoch = int(time.time())
        if cur.rowcount < 1:
            if level < 0:
                serv_notice(whodidit, "Account %s does not exist." % (user))
            else:
                cur.execute("INSERT INTO users (admin,access,added,bywho) VALUES (%s, %s, %s, %s)", (user, level, epoch, bywho))
                pgconn.commit()
                serv_notice(whodidit, "Account %s has been added with access %d." % (user, level))
        else:
            if level < 0:
                cur.execute("DELETE FROM users * WHERE admin = %s", [user])
                pgconn.commit()
                serv_notice(whodidit, "Access for account %s has been deleted." % (user))
            else:
                cur.execute("UPDATE users SET access = %s, bywho = %s, added = %s WHERE admin = %s", (level, bywho, epoch, user))
                pgconn.commit()
                serv_notice(whodidit, "Account %s has been updated to access %d." % (user, level))
    else:
        serv_notice(whodidit, "Access levels must be an integer.")

def get_acc(numnick, userlist):
    authed = 0
    access = 0
    for i in userlist:
        account = i.split(":")[0]
        ircnum = i.split(":")[1]
        if ircnum == numnick:
            return account

def access_level(numnick, userlist):
    from bot import *
    from commands import serv_notice
    authed = 0
    access = 0
    for i in userlist:
        account = i.split(":")[0]
        ircnum = i.split(":")[1]
        if ircnum == numnick:
            authed += 1
    if authed == 0:
        serv_notice(numnick, "You must first authenticate with NickServ.")
    else:
        cur.execute("SELECT access FROM users WHERE admin = %s", [account])
        access = cur.fetchone()
        if access is not None:
            return access[0]
        else:
            serv_notice(numnick, "You must first authenticate with NickServ.")
            return False
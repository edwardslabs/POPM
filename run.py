import config
import os
import signal
import string
import sys
import time

class StartServer(object):
    def __init__(self):
        if '-f' not in str(sys.argv):
            self.foreground = True
        else:
            self.foreground = False
        self.pidfile = str(os.path.dirname(os.path.realpath(__file__))) + "/popm.pid"
        self.fpid = None
        self.startTime = time.time()

    def is_forked(self):
        if not self.foreground:
            return "Running in foreground"
        else:
            return "Running in background"

    def get_pid(self):
        f = open(self.pidfile, "r")
        words = 0
        for line in f:
            words += 1
            try:
                pid = int(line)
            except:
                return "Unknown"
        if words == 0:
            return "Unknown"
        try:
            os.kill(pid, 0)
        except OSError:
            return "Unknown"
        else:
            return "%s" % (str(pid))

    def delpid(self):
        os.remove(self.pidfile)

    def is_process_running(self):
        f = open(self.pidfile, "r")
        words = 0
        for line in f:
            words += 1
            try:
                pid = int(line)
            except:
                return False
        if words == 0:
            return False
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            sys.exit("POPM is already running under PID %s" % (pid))

    def run(self, argv):
        config.dbverify()
        config.socketverify()
        if os.path.isfile(self.pidfile) and '-h' not in str(sys.argv):
            self.is_process_running()
        if '-h' in str(sys.argv):
            print ""
            print "POPM - Python Open Proxy Monitor"
            print "Run time arguments:"
            print "-h | Shows this help prompt"
            print "-f | Runs POPM in foreground mode"
            print ""
            print "If no arguments are given, POPM will run"
            print "as a back ground process."
            print ""
            sys.exit()
        elif '-f' in str(sys.argv):
            print "Starting POPM...."
            file(self.pidfile, 'w').write(str(os.getpid()))
            print "Now running in foreground mode"
            self.startprotocol()
        else:
            self.fpid = os.fork()
            if self.fpid != 0:
                print "Starting POPM...."
                file(self.pidfile, 'w').write(str(self.fpid))
                print "Forking into background under PID %d" % (self.fpid)
                sys.exit()
            self.startprotocol()

    def logger(self, importance, inputs):
        if importance <= config.DEBUG_LEVEL:
            if not self.foreground:
                print(inputs)

    def startprotocol(self):
        config.dbconnect()
        if config.PROTO.lower() == "p10server":
                import p10server
                boot_time = int(time.time())
                config.confproto.connect(boot_time)
                config.confproto.loadclient(0, boot_time, config.BOT_NAME, config.BOT_HOST, config.BOT_MODE, config.SERVER_NUMERIC, config.BOT_DESC)
                config.confproto.joinchannel(boot_time, "A", config.DEBUG_CHANNEL)
                config.confproto.eob()
                config.confproto.startbuffer()

if __name__ == "__main__":
    start = StartServer()
    start.run(sys.argv[1:])
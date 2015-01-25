import sys
import os
import signal
import string
import time

class StartServer(object):
    def __init__(self):
        if '-f' not in str(sys.argv):
            self.foreground = True
        else:
            self.foreground = False
        self.pidfile = str(os.path.dirname(os.path.realpath(__file__))) + "/popm.pid"

    def is_process_running(self):
        f = open(self.pidfile, "r")
        for line in f:
            try:
                pid = int(line)
            except:
                return False
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    def run(self, argv):
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
            pid = str(os.getpid())
            if os.path.isfile(self.pidfile):
                if self.is_process_running():
                    sys.exit("POPM is already running.")
                else:
                    file(self.pidfile, 'w').write(pid)
            else:
                file(self.pidfile, 'w').write(pid)
            print "Starting POPM...."
            print "Now running in foreground mode"
            self.startprotocol()
        else:
            fpid = os.fork()
            if fpid != 0:
                print "Starting POPM...."
                spid = str(fpid)
                if os.path.isfile(self.pidfile):
                    if self.is_process_running():
                        print "POPM is already running."
                        os.kill(fpid, signal.SIGTERM)
                        os.kill(os.getpid(), signal.SIGTERM)
                    else:
                        file(self.pidfile, 'w').write(spid)
                else:
                    file(self.pidfile, 'w').write(spid)
                print "Forking into background under PID %d" % (fpid)
                sys.exit()
            self.startprotocol()

    def logger(self, importance, inputs):
        import config
        if importance <= config.DEBUG_LEVEL:
            if not self.foreground:
                print(inputs)

    def startprotocol(self):
        import config
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
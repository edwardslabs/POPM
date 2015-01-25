import sys
import os
import string
import time

class StartServer(object):
    def __init__(self):
        if '-f' not in str(sys.argv):
            self.foreground = True
        else:
            self.foreground = False

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
            curdir = os.path.dirname(os.path.realpath(__file__))
            pidfile = curdir + "/popm.pid"
            if os.path.isfile(pidfile):
                os.remove(pidfile)
                file(pidfile, 'w').write(pid)
            else:
                file(pidfile, 'w').write(pid)
            self.startprotocol()
        else:
            fpid = os.fork()
            if fpid != 0:
                print "Starting POPM...."
                print "Forking into background under PID %d" % (fpid)
                spid = str(fpid)
                curdir = os.path.dirname(os.path.realpath(__file__))
                pidfile = curdir + "/popm.pid"
                if os.path.isfile(pidfile):
                    os.remove(pidfile)
                    file(pidfile, 'w').write(spid)
                else:
                    file(pidfile, 'w').write(spid)
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
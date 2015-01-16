def signal_handler(signal, frame):
	import sys
	from config import *
	from server import *
	s.send("%sAAA Q :Exiting on signal %s\n" % (SERVER_NUMERIC, signal))
	print("[WRITE]: %sAAA Q :Exiting on signal %s" % (SERVER_NUMERIC, signal))
	s.send("%s SQ %s 0 :Exiting on signal %s\n" % (SERVER_NUMERIC, SERVER_HOST_NAME, signal))
	print("[WRITE]: %s SQ %s 0 :Exiting on signal %s" % (SERVER_NUMERIC, SERVER_HOST_NAME, signal))
	sys.exit(0)
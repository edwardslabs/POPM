class Signals:
	def signal_handler(self, signal, frame):
		import config
		import server
		conf = config.Config()
		serv = server.Server()
		serv.send("%sAAA Q :Exiting on signal %s\n" % (conf.SERVER_NUMERIC, signal))
		print("[WRITE]: %sAAA Q :Exiting on signal %s" % (conf.SERVER_NUMERIC, signal))
		serv.send("%s SQ %s 0 :Exiting on signal %s\n" % (conf.SERVER_NUMERIC, conf.SERVER_HOST_NAME, signal))
		print("[WRITE]: %s SQ %s 0 :Exiting on signal %s" % (conf.SERVER_NUMERIC, conf.SERVER_HOST_NAME, signal))
		sys.exit(0)
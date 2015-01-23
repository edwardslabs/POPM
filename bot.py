import sys
import socket
import string
import signal
import time
import config
from proxy import DNSBL, getTrueIP
from settings import is_settable, get_set, update_settings, get_set_value, get_dnsbl_value, get_http_value, get_socks_value, isExempt, checkexpired
from multiprocessing import Process, Queue

if __name__ == "__main__":
    if config.PROTO.lower() == "p10server":
        import p10server
        boot_time = int(time.time())
        config.confproto.connect(boot_time)
        config.confproto.loadclient(0, boot_time, config.BOT_NAME, config.BOT_HOST, config.BOT_MODE, config.SERVER_NUMERIC, config.BOT_DESC)
        config.confproto.joinchannel(boot_time, "A", config.DEBUG_CHANNEL)
        config.confproto.eob()
        config.confproto.startbuffer()
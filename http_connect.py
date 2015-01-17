from server import *
from bot import *
from settings import *

def http_connect(ip):
    import socket
    import socks
    from threading import Thread
    from thread import start_new_thread, allocate_lock
    sockfunc = socks.Sock()
    info = dnsbl.DNSBL()
    num_threads = 0
    thread_started = False
    lock = allocate_lock()
    contrue = 0
    if info.ENABLE_HTTP == 0:
        sockfunc.sockscheck(ip)
    else:
        global num_threads, thread_started, contrue
        testhost = "blindsighttf2.com:80"
        ports = [80,81,1075,3128,4480,6588,7856,8000,8080,8081,8090,7033,8085,8095,8100,8105,8110,1039,1050,1080,1098,11055,1200,19991,3332,3382,35233,443,444,4471,4480,5000,5490,5634,5800,63000,63809,65506,6588,6654,6661,6663,6664,6665,6667,6668,7070,7868,808,8085,8082,8118,8888,9000,9090,9988]

        def http_connect_threads(ip, port):
            global num_threads, thread_started, contrue
            lock.acquire()
            num_threads += 1
            thread_started = True
            lock.release()
            tcp=socket.socket()
            tcp.settimeout(2)
            portbuf = ""
            try:
                tcp.connect((ip, port))
                tcp.send("CONNECT %s HTTP/1.0\r\n\r\n" % (ip))
                #print "[~~~MADE IT PAST TRY~~~]"
                inttime1 = int(time.time())
                inttime2 = int(time.time())
                while inttime2 - inttime1 < 2:
                    inttime2 = int(time.time())
                    data = tcp.recv(1024)
                    if data is not False and "HTTP/1.0 200 OK" in data:
                        s.send("%s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]\n" % (SERVER_NUMERIC, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
                        print("[WRITE][HTTP_CONNECT]: %s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]" % (SERVER_NUMERIC, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
                        contrue += 1
                        tcp.close()
                        break
            except socket.error, v:
                #print "[CONNERR (%s) %s]" % (port, v)
                pass
            lock.acquire()
            num_threads -= 1
            lock.release()

        def https_connect_threads(ip, port):
            global num_threads, thread_started, contrue
            lock.acquire()
            num_threads += 1
            thread_started = True
            lock.release()

            tcps=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ssl_sock = ssl.wrap_socket(tcps)

            ssl_sock.settimeout(2)
            portbuf = ""
            try:
                ssl_sock.connect((ip, port))
                ssl_sock.send("CONNECT %s HTTP/1.0\r\n\r\n" % (ip))
                #print "[~~~SSL MADE IT PAST TRY~~~]"
                inttime1 = int(time.time())
                inttime2 = int(time.time())
                while inttime2 - inttime1 < 2:
                    inttime2 = int(time.time())
                    data = ssl_sock.recv(1024)
                    if data is not False and "HTTP/1.0 200 OK" in data:
                        s.send("%s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]\n" % (SERVER_NUMERIC, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
                        print("[WRITE][HTTP_CONNECT]: %s GL * +*@%s 259200 %d %d :AUTO Using or hosting open proxies is not permitted on %s. [Detected http_connect/%s]" % (SERVER_NUMERIC, ip, int(time.time()), int(time.time()) + 259200, NETWORK_NAME, port))
                        contrue += 1
                        ssl_sock.close()
                        break
            except socket.error, v:
                #print "[SSL CONNERR (%s) %s]" % (port, v)
                pass
            lock.acquire()
            num_threads -= 1
            lock.release()

        for newport in ports:
            start_new_thread(http_connect_threads, (ip, newport, ))
            start_new_thread(https_connect_threads, (ip, newport, ))

        while not thread_started:
            pass
        while num_threads > 0:
            pass

        if str(contrue) == "0" or contrue is None:
            sockfunc.sockscheck(ip)
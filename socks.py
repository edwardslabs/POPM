class Sock:
    def sockscheck(ip):
        num_threads = 0
        thread_started = False
        lock = allocate_lock()
        contrue = 0
        if ENABLE_SOCKS != 0:
            global num_threads, thread_started, contrue
            ports = [1080,1075,10000,10080,10099,10130,10242,10777,1025,1026,1027,1028,1029,1030,1031,1032,1033,1039,1050,1066,1081,1098,11011,11022,11033,11055,11171,1122,11225,1180,1182,1200,1202,1212,1234,12654,1337,14841,16591,17327,1813,18888,1978,1979,19991,2000,21421,22277,2280,24971,24973,25552,25839,26905,28882,29992,3127,3128,32167,3330,3380,34610,3801,3867,40,4044,41080,41379,43073,43341,443,44548,4471,43371,44765,4914,49699,5353,559,58,6000,62385,63808,6551,6561,6664,6748,6969,7007,7080,8002,8009,8020,8080,8085,8111,8278,8751,8888,9090,9100,9988,9999,59175,5001,19794]

            def check_socks(ip, port):
                global num_threads, thread_started, contrue
                lock.acquire()
                num_threads += 1
                thread_started = True
                lock.release()

                try:
                    sen = struct.pack('BBB', 0x05, 0x01, 0x00)
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(( ip , int( port )  ))
                    s.sendall(sen)
                    data = s.recv(2)
                    s.close()
                    version, auth = struct.unpack('BB', data)
                    print 'server : port  is  ', ip, ':', port, '; varsion: ', version
                except Exception as e:
                    print e

                lock.acquire()
                num_threads -= 1
                lock.release()

            for newport in ports:
                start_new_thread(check_socks, (ip, newport, ))

            while not thread_started:
                pass
            while num_threads > 0:
                pass
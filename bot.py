import sys
import socket
import ssl
import string
import signal
import time
import re
import datetime
import dns.resolver
import httplib
import socks
import struct
import urllib2
import psycopg2
import yaml
import access
import server
from config import *
from threading import Thread
from thread import start_new_thread, allocate_lock

pgconn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
cur = pgconn.cursor()
# Have cursor dedicated for settings look ups #
pgconnauto = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME, DB_USER, DB_HOST, DB_PASS))
curauto = pgconnauto.cursor()

curauto.execute("SELECT enable_dnsbl,enable_http,enable_socks,access_die,access_set FROM settings")
for row in curauto.fetchall():
    ENABLE_DNSBL = row[0]
    ENABLE_HTTP = row[1]
    ENABLE_SOCKS = row[2]
    ACCESS_DIE = row[3]
    ACCESS_SET = row[4]
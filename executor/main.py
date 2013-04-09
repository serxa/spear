#!/usr/bin/env python
#-*- encoding: utf-8 -*-

"""Executor module of SPEAR system"""

import BaseHTTPServer
import httplib
import json
import os
import sqlite3
import ssl
import threading
import time
from functools import partial
from sys import argv, exit

import settings
from httphandler import ExecutorHandler
from processes_db import ProcessesTable

def server_thread(): # TODO: move to httphandler.py
    """Executor/http-server thread"""
    proc = ProcessesTable(settings.DATABASE_FILE)
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((settings.HOST_NAME, settings.PORT_NUMBER), partial(ExecutorHandler, proc))
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile = settings.CERTFILE, server_side = True, cert_reqs = ssl.CERT_NONE)
    httpd.serve_forever()
    # Will never happen
    httpd.server_close()

def heart_thread():
    """Executor/heartbeat-sender thread"""
    proc = ProcessesTable(settings.DATABASE_FILE)
    while True:
        #TODO: section below should be executed on timer call
        rows = proc.execute('SELECT * FROM @table WHERE gversion < lversion')
        tasks = [proc._a2d(row) for row in rows]
        data = json.dumps({'port' : settings.PORT_NUMBER, 'tasks' : tasks})
        http_conn = httplib.HTTPSConnection(settings.SERVER_HOST, settings.SERVER_PORT, timeout = settings.CONNECTION_TIMEOUT)
        headers = {'Content-Type' : 'application/json', 'Content-Length' : len(data)}
        try:
            http_conn.request('POST', '/hb?eid={0}'.format(settings.EID), data, headers)
            response = http_conn.getresponse()
            resp_data = json.load(response)
            if resp_data['success'] == True:
                proc.execute('''UPDATE @table SET gversion = lversion WHERE gversion < lversion''')
                proc.commit()
        except IOError:
            pass
        http_conn.close()
        time.sleep(settings.HEARTBEAT_INTERVAL)

if __name__ == '__main__':
    if '--help' in argv or '-h' in argv:
        print 'Usage: {0} ARG1=VAL1 ARG2=VAL2'.format(argv[0])
        print
        print 'Available args:'
        docs = [a[:-4] for a in dir(settings) if a.endswith('_DOC')]
        docs.sort()
        width = max(len(i) for i in docs) + 1
        for a in docs:
            print '{0:<{width}}: {1}'.format(a, getattr(settings, a+'_DOC'), width = width)
        exit(0)

    # Process command-line arguments
    for a in argv[1:]:
        try:
            f, v = a.split('=', 1)
        except ValueError:
            print 'Unknown argument: `{0}`'.format(a)
            print 'Please use \'-h\' ot \'--help\''
            print 'Goodbye'
            exit(0)
        else:
            setattr(settings, f, v)

    # List of function which will be started in separate threads
    thread_functions = [server_thread, heart_thread]
    # Create thread objects
    threads = [threading.Thread(target = f) for f in thread_functions]
    # Start them
    for t in threads:
        t.start()
    # Wait for Ctrl-C # TODO : remove in production
    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        os._exit(0)


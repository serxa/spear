#!/usr/bin/env python
#-*- encoding: utf-8 -*-

"""Executor module of SPEAR system

"""

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

def server_thread(database_factory): # TODO: move to httphandler.py
    """Executor/http-server thread
    """
    proc = database_factory()
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((settings.HOST_NAME, settings.PORT_NUMBER), partial(ExecutorHandler, proc))
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile = settings.CERTFILE, server_side = True, cert_reqs = ssl.CERT_NONE)
    httpd.serve_forever()
    # Will never happen
    httpd.server_close()

def heart_thread(database_factory):
    """Executor/heartbeat-sender thread
    """
    proc = database_factory()
    while True:
        #TODO: section below should be executed on timer call
        rows = proc.execute('SELECT * FROM @table WHERE gversion < lversion')
        tasks = [proc._a2d(row) for row in rows]
        data = json.dumps({'port' : settings.PORT_NUMBER, 'tasks' : tasks})
        http_conn = httplib.HTTPSConnection(settings.SERVER_HOST, settings.SERVER_PORT, timeout = settings.CONNECTION_TIMEOUT) # TODO: Test whether this works with HTTPS
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
        time.sleep(settings.HEARTBEAT_TIME)

if __name__ == '__main__':
    # Pepare database connection
    # We will need separate database connections for each thread
    database = partial(ProcessesTable, settings.DATABASE_FILE)
    # List of function which will be started in separate threads
    thread_functions = [server_thread, heart_thread]
    # Create thread object with these functions
    threads = [threading.Thread(target = f, args = (database,)) for f in thread_functions]
    # Start them
    for t in threads:
        # t.daemon = True # It won't make a `true` daemon anyway
        t.start()
    # Wait for Ctrl-C # TODO : remove in production
    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        os._exit(0)

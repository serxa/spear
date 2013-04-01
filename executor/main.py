#!/usr/bin/env python
#-*- encoding: utf-8 -*-

"""Executor module of SPEAR system

"""

import BaseHTTPServer
import ssl
import sqlite3
import threading
import os
import time
import httplib
import json
from sys import argv, exit
from functools import partial

from httphandler import ExecutorHandler
import settings

def server_thread(database): # TODO: move to httphandler.py
    """Executor/http-server thread
    """
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((settings.HOST_NAME, settings.PORT_NUMBER), partial(ExecutorHandler, database))
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=settings.CERTFILE, server_side=True, cert_reqs = ssl.CERT_NONE)
    httpd.serve_forever()
    # Will never happen
    httpd.server_close()

def heart_thread(database):
    """Executor/heartbeat-sender thread
    """
    c = database.cursor()
    rows = c.execute('''pragma table_info(processes)''') # TODO: execute only once
    info = [i[1] for i in rows]
    #TODO: section below should be executed on timer call
    rows = c.execute('''SELECT * FROM processes WHERE gversion < lversion''')
    tasks = []
    for task in rows:
        t = dict()
        for (f,l) in zip(task, info):
            t[l] = f
        tasks.append(t)
    data = {'port' : settings.PORT_NUMBER, 'tasks' : tasks}
    http_conn = httplib.HTTPSConnection(settings.SERVER_HOST, settings.SERVER_PORT, timeout = settings.CONNECTION_TIMEOUT) # TODO: Test whether this works with HTTPS
    headers = {'Content-Type' : 'application/json'}
    try:
        http_conn.request('POST', headers, json.dumps(data))
        response = http_conn.getresponse()
        resp_data = response.read()
        if resp_data['success']==True:
            rows = c.execute('''UPDATE processes SET gversion = lversion WHERE gversion < lversion''')
    except IOError:
        http_conn.close()
        pass
    http_conn.close()



if __name__ == '__main__':
    # Pepare database connection
    # We will need separate database connections for each thread
    database = partial(sqlite3.connect, settings.DATABASE_FILE)
    # List of function which will be started in separate threads
    thread_functions = [server_thread, heart_thread]
    # Create thread object with these functions
    threads = [threading.Thread(target = f, args = (database(),)) for f in thread_functions]
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

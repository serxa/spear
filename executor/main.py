#!/usr/bin/env python
#-*- encoding: utf-8 -*-

"""Executor module of SPEAR system"""

import BaseHTTPServer
import httplib
import json
import logging
import os
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
    logging.debug('Starting server thread')
    proc = ProcessesTable(settings.DATABASE_FILE)
    logging.debug('Server thread initialized')
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((settings.HOST_NAME, settings.PORT_NUMBER), partial(ExecutorHandler, proc))
    logging.debug('Enabling SSL')
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile = settings.CERTFILE, server_side = True, cert_reqs = ssl.CERT_NONE)
    logging.info('Starting HTTP server')
    httpd.serve_forever()
    # Will never happen
    logging.critical('HTTP server suddenly stopped, though it should never do it!')
    httpd.server_close()

def heart_thread():
    """Executor/heartbeat-sender thread"""
    logging.debug('Starting heartbeater thread')
    proc = ProcessesTable(settings.DATABASE_FILE)
    while True:
        #TODO: section below should be executed on timer call
        logging.debug('Rerieving info from database')
        rows = proc.execute('SELECT * FROM @table WHERE gversion < lversion')
        tasks = [proc._a2d(row) for row in rows]
        logging.info('Sending %d tasks in heartbeat', len(tasks))
        data = json.dumps({'port' : settings.PORT_NUMBER, 'tasks' : tasks})
        http_conn = httplib.HTTPSConnection(settings.SERVER_HOST, settings.SERVER_PORT, timeout = settings.CONNECTION_TIMEOUT)
        headers = {'Content-Type' : 'application/json', 'Content-Length' : len(data)}
        try:
            logging.debug('Connecting to server...')
            http_conn.request('POST', '/hb?eid={0}'.format(settings.EID), data, headers)
            response = http_conn.getresponse()
            resp_data = json.load(response)
            if resp_data['success'] == True:
                logging.debug('Heartbeat sent succesfully')
                proc.execute('''UPDATE @table SET gversion = lversion WHERE gversion < lversion''')
                proc.commit()
            else:
                logging.warning('Server could not accept heartbeat: %s', response)
                logging.debug('Heartbeat content: """%s"""', data)
        except IOError:
            logging.warning('Unable to contact heartbeat server')
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
            print '{0:<{width}}: {1} [default: {2}]'.format(a, getattr(settings, a+'_DOC'), getattr(settings, a), width = width)
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

    # Set up logging
    logging.basicConfig(filename = settings.LOG_FILE, level = getattr(logging, settings.LOG_LEVEL.upper()), format = '%(asctime)s %(levelname)8s <%(threadName)s::%(name)s> - %(message)s')
    logging.info('Starting executor as %s', str(argv))
    # List of function which will be started in separate threads
    # Some request handlers, especially /proc/start are NOT thread safe, so there should never be more then one HTTPRequestHandler thread
    thread_functions = [server_thread, heart_thread]
    # Create thread objects
    threads = [threading.Thread(target = f, name = f.__name__) for f in thread_functions]
    # Start them
    for t in threads:
        t.start()
    logging.debug('Threads started')
    # Wait for Ctrl-C # TODO : remove in production
    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        logging.info('Interrupted by keystroke')
        os._exit(0)


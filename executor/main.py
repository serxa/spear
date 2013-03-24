#!/usr/bin/env python
#-*- encoding: utf-8 -*-

"""Executor module of SPEAR system

"""

import BaseHTTPServer
import sqlite3
import threading
import os
import time
from sys import argv, exit
from functools import partial

from httphandler import ExecutorHandler
import settings

def server_thread(database):
    """Executor/http-server thread
    """
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((settings.HOST_NAME, settings.PORT_NUMBER), partial(ExecutorHandler, database))
    httpd.serve_forever()
    # Will never happen
    httpd.server_close()

def heart_thread(database):
    """Executor/heartbeat-sender thread
    """
    pass


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


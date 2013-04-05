#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from sys import argv, exit
import BaseHTTPServer
import cgi
import json
import ssl
import sys
import time

HOST_NAME = 'localhost'
PORT_NUMBER = 8013

class DummyHeartbeatHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(500)
        self.end_headers()
    def do_POST(self):
        """Respond to a POST request."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        datalen = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(datalen))
        print 'Port = {0}; updated_tasks = {1}'.format(data['port'], [i['tid'] for i in data['tasks']])
        sys.stdout.flush()

        self.wfile.write(json.dumps({'success' : True}))

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), DummyHeartbeatHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile = '../test_cert.pem', server_side = True, cert_reqs = ssl.CERT_NONE)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)


#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from sys import argv, exit

import time
import BaseHTTPServer
import json
import urlparse

import handlers


HOST_NAME = 'localhost' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8042

class ParserException(StandardError):
    pass

class ExecutorHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(500)
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "application/json")
        s.send_header("Server", "spear-executor 0.0.0.0.0.1")
        s.end_headers()
        url = urlparse.urlparse(s.path)
        try:
            urlpath = url.path.split('/')[1:]
            if len(urlpath) != 2:
                raise ParserException("Wrong URL structure")
            urlmodule = urlpath[0]
            urlfunc   = urlpath[1]
            urlargs   = urlparse.parse_qs(url.query)

            try:
                mod = getattr(handlers, urlmodule)
            except AttributeError:
                raise ParserException('Unable to find module')

            try:
                func = getattr(mod, urlfunc)
            except AttributeError:
                raise ParserException('Unable to find function')

            try:
                retval = func(**urlargs)
            except handlers.HandlerError as e:
                raise ParserException(e.message) # Just propagate error upwards
        except ParserException as e:
            s.wfile.write(json.dumps({'success':False, 'path': url, 'error': e.message}))
        else:
            s.wfile.write(json.dumps({'success':True, 'data':retval}))


if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), ExecutorHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)


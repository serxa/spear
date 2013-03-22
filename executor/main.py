#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from sys import argv, exit

import time
import BaseHTTPServer
import cgi
import json
import urlparse

import handlers


HOST_NAME = 'localhost' # TODO: Read from configfile
PORT_NUMBER = 8042

class ParserException(StandardError):
    pass

class ExecutorHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version='spear-executor/0.0.0.0.1'

    def do_HEAD(self):
        self.send_response(500)
        self.end_headers()

    def do_POST(self):
        """Respond to POST request."""
        ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
        post = cgi.parse_multipart(self.rfile,pdict)
        self.do_ANYTHING(post)

    def do_GET(self):
        """Respond to a GET request."""
        self.do_ANYTHING(dict())

    def do_ANYTHING(self, post):
        """Respond to request with accompanying POST data, if any"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        url = urlparse.urlparse(self.path)
        try:
            urlpath = url.path.split('/')[1:]
            if len(urlpath) != 2:
                raise ParserException("Wrong URL structure")
            urlmodule = urlpath[0]
            urlfunc   = urlpath[1]
            urlargs   = urlparse.parse_qs(url.query)
            urlargs['post'] = post

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
            self.wfile.write(json.dumps({'success':False, 'error': e.message}))
        else:
            self.wfile.write(json.dumps({'success':True, 'data':retval}))


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


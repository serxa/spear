#-*- encoding: utf-8 -*-

"""BaseHTTPServer.BaseHTTPRequestHandler class overload for spear-executor"""

import BaseHTTPServer
import cgi
import json
import logging
import traceback
import urlparse

import handlers

class ParserError(StandardError):
    pass

class ExecutorHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = 'spear-executor'
    proc_table = None
    def __init__(self, proc_table, *args, **kwargs):
        self.proc_table = proc_table
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_HEAD(self):
        self.send_response(500)
        self.end_headers()

    def do_POST(self):
        """Respond to POST request"""
        ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
        post = cgi.parse_multipart(self.rfile,pdict)
        self.do_ANYTHING(post)

    def do_GET(self):
        """Respond to a GET request"""
        self.do_ANYTHING(dict())

    def do_ANYTHING(self, post): # Not a conventional HTTPRequestHandler function, just a very handy routine
        """Respond to request with accompanying POST data, if any"""
        url = urlparse.urlparse(self.path)
        logging.info('Request from %s : %s', self.client_address[0], self.path)
        try:
            urlpath = url.path.split('/')[1:]
            if len(urlpath) != 2:
                raise ParserError("Wrong URL structure")
            urlmodule = urlpath[0]
            urlfunc   = urlpath[1]
            urlargs   = urlparse.parse_qs(url.query)
            urlargs['post'] = post

            try:
                mod = getattr(handlers, urlmodule)
            except AttributeError:
                raise ParserError('Unable to find module')

            try:
                func = getattr(mod, urlfunc)
            except AttributeError:
                raise ParserError('Unable to find function')
            logging.debug('Calling %s.%s', urlmodule, urlfunc)
            try:
                retval = func(self.proc_table, **urlargs)
            except handlers.HandlerError as e:
                raise ParserError(e.message) # Just propagate error upwards
        except ParserError as e:
            logging.info('Normal error while processing request: %s', e.message)
            self.send_response(500)
            self.send_header("Status", "error: "+e.message)
            self.end_headers()
        except Exception as e:
            logging.exception('Unexpected error processing request') # The expection info will be printed automatically
            raise
        else:
            logging.info('Request processed succesfully')
            self.send_response(200)
            self.send_header("Status", "success")
            if retval[0]: # JSON
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(retval[1]))
            else: # BINARY
                self.send_header("Content-type", "application/octet-stream")
                self.end_headers()
                self.wfile.write(retval[1])

    def log_message(self, format, *args):
        return # Silence!


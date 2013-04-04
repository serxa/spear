#-*- encoding: utf-8 -*-
"""Module for running and managing external executables"""

import multiprocessing
import os
from StringIO import StringIO # Probably use cStringIO?
import struct
import subprocess
import tempfile
import threading
import time

from exception import HandlerError

def run(database, **kwargs):
    try:
        wd = kwargs['wd'][0]
        executable = kwargs['exec'][0]
    except KeyError:
        raise HandlerError('Process parameters not specified')
    try:
        args = kwargs['arg']
    except KeyError:
        args = []
    try:
        timeout = float(kwargs['timeout'][0])
    except KeyError:
        timeout = 10 # Seconds
    try:
        stdinf = kwargs['stdin'][0]
    except KeyError:
        try:
            stdin = tempfile.TemporaryFile()
            stdin.write(kwargs['post']['stdin'][0])
            stdin.seek(0)
        except KeyError:
            stdin = None
    else:
        stdin = open(stdinf)

    stdout = tempfile.TemporaryFile()
    stderr = tempfile.TemporaryFile()
    argv = [executable]
    argv.extend(args)

    # subprocess module has no wait-with-timeout functionality, so helper thread is used
    try:
        proc = subprocess.Popen(argv, stdin = stdin, stdout = stdout, stderr = stderr, cwd = wd)
    except OSError:
        raise HandlerError('Unable to run')
    waiter_thread = threading.Thread(target = proc.communicate)
    waiter_thread.start()
    waiter_thread.join(timeout)
    if waiter_thread.is_alive():
        proc.terminate()
        waiter_thread.join()
        raise HandlerError('Timeout')
    exitcode = proc.returncode

    # TODO: probably use https://github.com/stendec/netstruct with '<BQ$Q$' format
    retdata = struct.pack('< B', exitcode)
    for f in [stdout, stderr]:
        f.seek(0, os.SEEK_END)
        retdata += struct.pack('Q', f.tell())
        f.seek(0)
        retdata += f.read()
    return (False, retdata)

# TODO: other functions


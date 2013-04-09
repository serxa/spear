#-*- encoding: utf-8 -*-
"""Module for running and managing external executables"""

import logging
import os
import struct
import subprocess
import sys
import tempfile
import threading
import time

from exception import HandlerError
from . import queues

TIMEOUT_DEFAULT = 10.0 # Seconds
logger = logging.getLogger('/proc')

def _stdin_from_request(**kwargs):
    try:
        stdinf = kwargs['stdin'][0]
    except KeyError:
        try:
            stdin = tempfile.TemporaryFile()
            stdin.write(kwargs['post']['stdin'][0])
            stdin.seek(0)
        except KeyError:
            stdin = open(os.devnull)
    else:
        stdin = open(stdinf)
    return stdin

def run(proc_table, **kwargs):
    try:
        wd = kwargs['wd'][0]
        executable = kwargs['exec'][0]
    except KeyError:
        raise HandlerError('Process parameters not specified')
    args = kwargs.get('arg', [])
    timeout = float(kwargs.get('timeout', [TIMEOUT_DEFAULT])[0]) #

    stdin  = _stdin_from_request(**kwargs)
    stdout = tempfile.TemporaryFile()
    stderr = tempfile.TemporaryFile()
    argv = [executable]
    argv.extend(args)

    # subprocess module has no wait-with-timeout functionality, so helper thread is used
    try:
        proc = subprocess.Popen(argv, stdin = stdin, stdout = stdout, stderr = stderr, cwd = wd)
    except OSError as e:
        logger.info('Unable to `run` process : %s', str(e))
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

def start(proc_table, **kwargs):
    try:
        wd = kwargs['wd'][0]
        executable = kwargs['exec'][0]
        queue = kwargs['queue_type'][0]
    except KeyError:
        raise HandlerError('Process parameters not specified')

    stdinf  = kwargs.get('stdin' ,[os.devnull])[0] #TODO: Only by-file method is supported
    stdoutf = kwargs.get('stdout',[os.devnull])[0]
    stderrf = kwargs.get('stderr',[os.devnull])[0]
    args = kwargs.get('arg', [])

    try:
        queueator = getattr(queues, queue)
    except AttributeError:
        raise HandlerError('Unable to find queueator')

    try:
        queueator.start(proc_table, executable, args, wd, stdinf, stdoutf, stderrf)
    except Exception, e:
        raise HandlerError('Error starting process: {0}'.format(str(e)))
    return (True, None)

def get(proc_table, **kwargs):
    try:
        tid = int(kwargs['tid'][0])
    except (KeyError, ValueError):
        raise HandlerError('TID not specified')

    try:
        proc = proc_table.get(tid)
    except KeyError as e:
        raise HandlerError(str(e))

    queue = proc.queue_type
    try:
        queueator = getattr(queues, queue)
    except AttributeError:
        raise HandlerError('Unable to find queueator')

    queueator.update(proc_table, tid)

    proc = proc_table.get(tid)

    return (True, proc.to_dict())

# TODO: other functions


#-*- encoding: utf-8 -*-
"""Module for handling various filesystem operations"""

import logging
import os
import time

from exception import HandlerError

logger = logging.getLogger('/fs')

def ftype(path):
    return 'dir' if os.path.isdir(path) else 'file'

def stat(proc_table, **kwargs):
    try:
        path = kwargs['path'][0]
    except KeyError:
        raise HandlerError('Path not specified')
    try:
        stat = os.stat(path)
    except OSError:
        raise HandlerError('Error accessing file')
    # TODO: return data as specified in docs
    return (True,
            {
            'path' : path,
            'size' : stat.st_size, # in bytes
            'mtime': stat.st_mtime,
            'ctime': stat.st_ctime,
            'isdir': os.path.isdir(path),
            'type' : ftype(path),
           })

def ls(proc_table, **kwargs):
    try:
        path = kwargs['path'][0]
    except KeyError:
        raise HandlerError('Path not specified')
    try:
        content = os.listdir(path)
        content.sort()
    except OSError:
        raise HandlerError('Unable to access file')
    return (True, [[f, ftype(os.path.join(path,f))] for f in content])

def mkdir(proc_table, **kwargs):
    try:
        path = kwargs['path'][0]
    except KeyError:
        raise HandlerError('Path not specified')
    try:
        os.mkdir(path)
    except OSError:
        raise HandlerError('Unable to access file')
    return (True, None)

def put(proc_table, **kwargs):
    try:
        path = kwargs['path'][0]
    except KeyError:
        raise HandlerError('Path not specified')
    try:
        filedata = kwargs['post']['file'][0]
    except KeyError:
        raise HandlerError('No POST data')
    try:
        f = open(path,'wb')
        f.write(filedata)
        f.close()
    except (OSError, IOError) as e:
        logger.info('Error `put`ing to file %s : %s', path, str(e))
        raise HandlerError('Error writing file')
    return (True, None)

def get(proc_table, **kwargs):
    try:
        path = kwargs['path'][0]
    except KeyError:
        raise HandlerError('Path not specified')
    try:
        data = open(path, 'rb').read()
    except (OSError, IOError) as e:
        logger.info('Error `get`ing file %s : %s', path, str(e))
        raise HandlerError('Error reading file')
    return (False, data)

# TODO: other functions


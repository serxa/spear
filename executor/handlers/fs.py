#-*- encoding: utf-8 -*-
"""Module for handling various filesystem operations"""

import os
import time
from exception import HandlerError

def stat(**kwargs):
    try:
        path = kwargs['path'][0]
    except KeyError:
        raise HandlerError('Path not specified')
    try:
        stat = os.stat(path)
    except OSError:
        raise HandlerError('Error accessing file')
    return {
            'path' : path,
            'size' : stat.st_size, # in bytes
            'mtime': stat.st_mtime,
            'ctime': stat.st_ctime,
            'isdir': os.path.isdir(path),
            'type' : {True: 'dir', False: 'file'}[os.path.isdir(path)],
           }


def ls(**kwargs):
    try:
        path = kwargs['path'][0]
    except KeyError:
        raise HandlerError('Path not specified')
    try:
        content = os.listdir(path)
    except OSError:
        raise HandlerError('Unable to access file')
    return [
            [f, stat(path = os.path.join(path,f))['type']] for f in content
           ]

def put(**kwargs):
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
    except OSError:
        raise HandlerError('Unable ro write file')


# TODO: other functions


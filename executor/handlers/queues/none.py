#-*- encoding: utf-8 -*-

"""The corner case of queue (no queue at all), as well as interface for queues-backends in general"""

import os
import resource
import select
import signal
import sys

PROCESS_DAEMONIZING_TIMEOUT = 5 # Seconds

class Process():
    """A class representing a process enrty in database"""
    STATUS_STARTING = 1
    STATUS_WAITING  = 2
    STATUS_RUNNING  = 3
    STATUS_ENDING   = 4
    STATUS_STOPPED  = 5

    def __init__(self, data = None):
        # For DB version 1
        self._dbversion = 1
        self._data = data
        self._from_tuple()

    def _from_tuple(self):
        if self._dbversion == 1:
            (self.tid, self.status, self.queue_type, self.pid, self.pgid, self.exitstatus, self.workdir, self.executable, self.args, self.queue_conf, self.stdin, self.stdout, self.stderr, self.lversion, self.gversion) = [None]*15 if self._data is None else self._data
        else:
            raise Exception('Unsupported database version')
    def _to_tuple(self):
        if self._dbversion == 1:
            self._data = (self.tid, self.status, self.queue_type, self.pid, self.pgid, self.exitstatus, self.workdir, self.executable, self.args, self.queue_conf, self.stdin, self.stdout, self.stderr, self.lversion, self.gversion)
        else:
            raise Exception('Unsupported database version')

    def insert(self, cursor):
        self.tid = None
        self._to_tuple()
        query = 'INSERT INTO processes VALUES ( {0} );'.format(' , '.join('?'*len(self._data)))
        cursor.execute(query, self._data)
    def update(self, cursor):
        rows = cursor.execute('''PRAGMA table_info(processes)''')
        info = [i[1] for i in rows]
        self._to_tuple()
        query = 'UPDATE processes SET {0} WHERE tid = ?;'.format(' , '.join('{0} = ?'.format(i) for i in info if i != 'tid'))
        cursor.execute(query, self._data[1:] + (self.tid,))
    def load(self, cursor):
        query = 'SELECT * FROM processes WHERE tid = ?;'
        cursor.execute(query, (self.tid,))
        self._data = cursor.fetchone()
        self._from_tuple()

def _is_readable_with_timeout(f, timeout):
    return len(select.select([f], [], [], timeout)[0]) > 0

def _close_all(minfd = 0):
    try:
        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        os.closerange(minfd, maxfd)
    except:
        pass

def start(database, executable, args, wd, stdinf, stdoutf, stderrf):
    """Fork correctly anmd start a process + add a record to database

    `stdin`, `stdout` and `stderr` parameters should be file names
    """
    pipe_r, pipe_w = os.pipe()
    stdin  = os.open(stdinf , os.O_RDONLY)
    stdout = os.open(stdoutf, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    stderr = os.open(stderrf, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    argv = [executable]
    argv.extend(args)
    try:
        pid = os.fork()
    except OSError, e:
        raise Exception('Unable to fork')
    if pid == 0:
        os.setsid()
        pid = os.fork() # Double edged fork !
        if pid == 0:
            try:
                os.chdir(wd)
                # Redirect IO
                os.dup2(stdin , 0)
                os.dup2(stdout, 1)
                os.dup2(stderr, 2)
                # Close file descriptors except for stdin/stdout/stderr
                _close_all(3)
                os.execvp(executable, argv)
            except Exception, e:
                print str(e)
                _close_all()
                os._exit(0)
        else:
            try:
                os.write(pipe_w, str(pid))
                os.close(pipe_w)
            except:
                pass
            os._exit(0)
    if not _is_readable_with_timeout(pipe_r, PROCESS_DAEMONIZING_TIMEOUT):
        raise Exception('No response from forked process')
    pgid = pid
    pid  = int(os.read(pipe_r, 42))
    os.close(pipe_r)
    p = Process(None)
    p.status      = p.STATUS_STARTING
    p.queue_type  = 'none'
    p.pid         = pid
    p.pgid        = pgid
    p.workdir     = wd
    p.executable  = executable
    p.args        = str(args)
    p.queueconf   = ''
    p.stdin       = stdinf
    p.stdout      = stdoutf
    p.stderr      = stderrf
    p.lversion    = 1
    p.gversion    = 0
    p.insert(database.cursor())
    database.commit()

def stop(database, tid):
    p = Process(None)
    p.tid = tid
    p.load(database.cursor())
    os.kill(p.pid, signal.SIGTERM)

def update(database, tid):
    p = Process(None)
    p.tid = tid
    p.load(database.cursor())
    if os.path.exists('/proc/{0}'.format(p.pid)):
        p.status = p.STATUS_RUNNING
    else:
        p.status = p.STATUS_STOPPED
    p.update(database.cursor())
    database.commit()


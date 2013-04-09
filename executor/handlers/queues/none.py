#-*- encoding: utf-8 -*-

"""The corner case of queue (no queue at all), as well as interface for queues-backends in general"""

import logging
import os
import resource
import select
import signal
import sys

PROCESS_DAEMONIZING_TIMEOUT = 5 # Seconds
logger = logging.getLogger('queue/none')

def _is_readable_with_timeout(f, timeout):
    """Return True when file descriptor `f` becomes readable within `timeout` seconds, otherwise False."""
    return len(select.select([f], [], [], timeout)[0]) > 0

def _close_all(minfd = 0):
    """Close all open file descriptors starting from `minfd`.

    Non-zero `minfd` might be used to preserve stdin/stdout/stderr.
    """
    try:
        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        os.closerange(minfd, maxfd)
    except:
        pass

def start(proc_table, executable, args, wd, stdinf, stdoutf, stderrf):
    """Fork correctly, start a process add a record to proc_table.

    `stdinf`, `stdoutf` and `stderrf` parameters should be file names.
    """
    pipe_r, pipe_w = os.pipe()
    stdin  = os.open(stdinf , os.O_RDONLY)
    stdout = os.open(stdoutf, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    stderr = os.open(stderrf, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    argv = [executable]
    argv.extend(args)
    logger.debug('`start`ing process %s 1>%s 2>%s <%s', str(argv), stdoutf, stderrf, stdinf)
    try:
        pid = os.fork()
    except OSError, e:
        logger.info('Error while forking: %s', e.message)
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
            os._exit(0) # Do waitpid and update database
    if not _is_readable_with_timeout(pipe_r, PROCESS_DAEMONIZING_TIMEOUT):
        logger.info('Forked process not responding within %d seconds', PROCESS_DAEMONIZING_TIMEOUT)
        raise Exception('No response from forked process')
    pgid = pid
    pid  = int(os.read(pipe_r, 42))
    os.close(pipe_r)
    logger.info('Started process PID=%d PGID=%d', pid, pgid)
    p = proc_table.new_row() # Create empty Process object
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
    proc_table.insert(p)

def stop(proc_table, tid):
    p = proc_table.get(tid)
    os.kill(p.pid, signal.SIGTERM)

def update(proc_table, tid):
    p = proc_table.get(tid)
    if os.path.exists('/proc/{0}'.format(p.pid)):
        p.status = p.STATUS_RUNNING
    else:
        p.status = p.STATUS_STOPPED
    proc_table.update(p)


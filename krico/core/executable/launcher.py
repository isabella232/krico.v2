"""Disk And Execution MONitor (Daemon)
Configurable daemon behaviors:
	1.) The current working directory set to the '/' directory.
	2.) The current file creation mode mask set to 0.
	3.) Close all open files (1024).
	4.) Redirect standard I/O streams to '/dev/null'.
A failed call to fork() now raises an exception.
References:
	1) Advanced Programming in the Unix Environment: W. Richard Stevens
	2) Unix Programming Frequently Asked Questions:
	http://www.erlenstar.demon.co.uk/unix/faq_toc.html
"""

import os

import krico.core.logger
import krico.core.configuration
import krico.core.stream
import krico.core.database

__author__ = 'Chad J. Schroeder'
__copyright__ = 'Copyright (C) 2005 Chad J. Schroeder'

__revision__ = '$Id$'
__version__ = '0.2'

_logger = krico.core.logger.get('krico.core.executable.launcher')
_configuration = krico.core.configuration.root


def launch(daemon_name):
    working_directory = _configuration.core.environment.resources
    umask = 0022
    max_fd = 1024
    output_redirect = '{}/{}.error.log'.format(_configuration.core.environment.logs, daemon_name)
    log_file = '{}/{}.log'.format(_configuration.core.environment.logs, daemon_name)

    # This is needed to avoid pymongo connection problems after forking process
    krico.core.database.connection.disconnect()

    try:
        pid = os.fork()
    except OSError, e:
        raise RuntimeError('{} [{}]'.format(e.strerror, e.errno))

    if pid == 0:
        os.setsid()

        try:
            pid = os.fork()  # Fork a second child.
        except OSError, e:
            raise RuntimeError('{} [{}]'.format(e.strerror, e.errno))

        if pid == 0:
            _logger.info('My daemon pid is: {}'.format(os.getpid()))
            os.chdir(working_directory)
            os.umask(umask)
        else:
            # _logger.info('First child: {}'.format(os.getpid()))
            _logger.info('Daemon started with PID: {}'.format(pid))
            os._exit(0)
    else:
        # _logger.info('Parent: {}'.format(os.getpid()))
        import time
        time.sleep(1)
        
        os._exit(0)  # Exit parent of the first child.

    import resource  # Resource usage information.
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if maxfd == resource.RLIM_INFINITY:
        maxfd = max_fd

    # Iterate through and close all file descriptors.
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:  # ERROR, fd wasn't open to begin with (ignored)
            pass

    if (hasattr(os, 'devnull')):
        stdinput = os.devnull
    else:
        stdinput = '/dev/null'

    os.open(stdinput, os.O_RDWR | os.O_APPEND)  # standard input (0)
    os.open(output_redirect, os.O_RDWR | os.O_APPEND | os.O_CREAT)  # standard output (1)
    os.dup2(1, 2)  # standard error (2)

    krico.core.stream.reset(open(log_file, 'w+'))

    return 0

import errno
import os
import os.path
import signal
import subprocess
import sys
import time

import krico.core.configuration
import krico.core.logger
import krico.core.exception
import krico.core.timestamp

__author__ = 'tziol'

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get('krico.core.process')


def is_alive(pid):
    _logger.debug('Checking if process is alive: {}'.format(pid))
    try:
        os.kill(pid, signal.SIG_DFL)

        _logger.debug('Process alive.')
        return True

    except OSError as err:
        if err.errno == errno.ESRCH:
            _logger.debug('Process not alive.')
            return False
        else:
            raise


def terminate(pids, timeout=5.0):
    _logger.info('Terminating processes: {}'.format(pids))

    alive_pids = filter(is_alive, pids)
    _logger.info('Alive processes: {}'.format(alive_pids))

    for pid in alive_pids:
        os.kill(pid, signal.SIGTERM)

    start = krico.core.timestamp.now()
    kill_sent = False

    while alive_pids:
        _logger.debug('Processes still alive: {}'.format(alive_pids))

        wait_time = (krico.core.timestamp.now() - start).total_seconds()

        if not kill_sent and wait_time > timeout:
            _logger.warn('Processes refuse to terminate, sending the KILL signal: '.format(alive_pids))
            for pid in alive_pids:
                os.kill(pid, signal.SIGKILL)

            kill_sent = True

        if wait_time > 2.0 * timeout:
            raise krico.core.exception.Error('Failed to stop processes: {}'.format(alive_pids))

        time.sleep(0.25)
        alive_pids = filter(is_alive, alive_pids)

    _logger.info('All processes terminated.')


def execute(command, environment_extra=None):
    _logger.info('Executing command: {}'.format(command))

    environment = os.environ.copy()
    if environment_extra:
        environment.update(environment_extra)

    _logger.debug('Environment:\n{}'.format(environment_extra))

    worker = None
    try:
        worker = subprocess.Popen(
            command,
            env=environment,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        return_code = worker.wait()

        _logger.debug('Return code: {}'.format(return_code))
        if return_code != 0:
            raise krico.core.exception.Error('Command terminated with non-zero exit code: {}'.format(return_code))

    except Exception as ex:
        _logger.error('Processing error: {}'.format(ex))
        if worker:
            try:
                worker.terminate()
            except OSError:
                pass

        raise ex

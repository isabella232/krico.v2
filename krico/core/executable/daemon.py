import os
import os.path

import krico.core.commander
import krico.core.configuration
import krico.core.debug
import krico.core.exception
import krico.core.logger
import krico.core.timestamp

import launcher
import process
import interrupt

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get(__name__)


class DaemonDispatcher(krico.core.commander.CommandDispatcher):
    # override in subclass
    _name = 'krico-daemon'

    @classmethod
    def start(cls):
        running_pid = cls.__running_pid()

        if running_pid:
            _logger.warn('Daemon already running as process {}, cannot start.'.format(running_pid))

        else:
            pid_file_path = None
            try:
                launcher.launch(cls._name)  # launching into the background void

                interrupt.attach()

                pid_directory = _configuration.core.environment.resources
                if not os.path.exists(pid_directory):
                    os.makedirs(pid_directory)

                pid = os.getpid()

                pid_file_path = cls.__pid_file_path()
                with open(pid_file_path, 'w') as pid_file:
                    pid_file.write(str(pid))

                _logger.info('Executing as process {}...'.format(pid))

                cls._execute()

            except interrupt.TerminateInterrupt:
                _logger.info('Daemon termination requested.')

            except:
                krico.core.debug.log_exception(_logger)
                raise

            finally:
                try:
                    if pid_file_path:
                        os.remove(pid_file_path)

                    interrupt.detach()

                except OSError as ex:
                    _logger.error('Error occured during daemon termination: {}'.format(ex))

    @classmethod
    def stop(cls):
        running_pid = cls.__running_pid()

        if not running_pid:
            _logger.warn('Daemon not running, cannot stop.')

        else:
            process.terminate([running_pid], 10.0)
            _logger.info('Daemon process terminated.')

    @classmethod
    def restart(cls):
        cls.stop()
        cls.start()

    @classmethod
    def run(cls):
        _logger.info('Running in the foreground...')
        cls._execute()

    @classmethod
    def __pid_file_path(cls):
        return '{}/{}.pid'.format(
            _configuration.core.environment.resources,
            cls._name
        )

    @classmethod
    def __running_pid(cls):
        pid_file_path = cls.__pid_file_path()

        if os.path.exists(pid_file_path):
            _logger.debug('PID file {} already exists.'.format(pid_file_path))

            with open(pid_file_path, 'r') as pid_file:
                existing_pid = int(pid_file.read())
                _logger.debug('Found existing PID in file: {}'.format(existing_pid))

                if process.is_alive(existing_pid):
                    _logger.debug('Daemon already running as process {}.'.format(existing_pid))
                    _logger.debug('My PID is {}.'.format(os.getpid()))
                    return existing_pid

        _logger.info('Daemon not running.')
        return None

    @classmethod
    def _execute(cls):
        raise NotImplementedError()

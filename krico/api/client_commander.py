import sys

import krico.core.commander
import krico.core.configuration
import krico.core.logger
import krico.api.client

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get(__name__)


class _Commander(krico.core.commander.CommandDispatcher):
    @classmethod
    def test_classify(cls):
        return NotImplementedError

    @classmethod
    def test_predict(cls):
        return NotImplementedError


def main():
    _Commander.dispatch_commandline()


if __name__ == '__main__':
    sys.exit(main())
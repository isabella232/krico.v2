import sys

import krico.core.commander
import krico.core.configuration
import krico.core.logger
import krico.client.api

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get(__name__)


class _Commander(krico.core.commander.CommandDispatcher):
    @classmethod
    def test_classify(cls):
        print krico.client.api.default.classify(
            instance_id='phase-3-science-hpcc-00023'
        )

    @classmethod
    def test_predict(cls):
        print krico.client.api.default.predict_load(
            image='bigdata-hadoop-wordcount',
            category='bigdata',
            parameters={
                'data': 32,
                'processors': 24,
                'memory': 32,
                'disk': 50
            }
        )


def main():
    _Commander.dispatch_commandline()


if __name__ == '__main__':
    sys.exit(main())

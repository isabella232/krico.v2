import pytest

from krico.core import init
from krico.core import logger


@pytest.fixture(scope="session", autouse=True)
def initialize_tests():
    init('config.yml')
    logger.init()

import pytest
import os

from krico.core import init
from krico.core import logger


@pytest.fixture(scope="session", autouse=True)
def initialize_tests():
    init(
        '{}/test_config.yml'.
        format(os.path.dirname(os.path.abspath(__file__))))
    logger.init()

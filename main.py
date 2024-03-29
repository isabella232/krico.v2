# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Main entry point.
Responsible for configuration and prepare components
and start service.
"""

import argparse

import core
from api import service
from core import logger


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--config',
        help="Configuration path",
        required=True
    )

    args = parser.parse_args()

    # Initialize all necessary objects.
    core.init(args.config)

    logger.init()

    # Run service.
    service.run()


if __name__ == '__main__':
    main()

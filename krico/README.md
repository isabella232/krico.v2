<!--
 Copyright (c) 2019 Intel Corporation

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

# ![Swan diagram](/images/swan-logo-48.png) Swan

## KRICO Experiment

This experiment uses KRICO (Komponent Rekomendacji dla Inteligentnych Chmur Obliczeniowych).

It consists of three sub experiments:
- Metric Gathering which provides data for KRICO neural network.
- Classification Experiment which runs workloads, gather metrics from them and in the end do classification.
- Prediction Experiment which for passed parameters do prediction.

More information about KRICO [krico.gda.pl](http://krico.gda.pl/)

## Architecture

### ![KRICO architecture](docs/images/krico-architecture.png)g

## Table of Contents
1. [Installation](docs/installation.md)
1. [Run the Experiment ](docs/run_experiment.md)
1. [Tune Mutilate & Memcached](docs/tuning.md)
1. [Troubleshooting](docs/troubleshooting.md)

## Appendix

1. [Important Experiment Flags](docs/experiment_configuration.md)
1. [All Experiment Flags](docs/experiment_config_dump_example.md)

## KRICO (Komponent Rekomendacji dla Inteligentnych Chmur Obliczeniowych)

KRICO is framework for workload classification and prediction of requiremenets to run workload.
More information about KRICO (in Polish) [krico.gda.pl](http://krico.gda.pl/)

---
### KRICO module exposes gRPC API

#### Classify
Classify workload.

Request message:
```
message ClassifyRequest {
    string instance_id = 1;
}
```
Response message:
```
message ClassifyResponse {
    string classified_as = 1;
}
```

#### Predict
Predict requirements for running workload on OpenStack cluster. 

Request message:
```
message PredictRequest {
    string category = 1;
    string image = 2;
    map<string, double> parameters = 3;
    string configuration_id = 4;
    string allocation_mode = 5;
}
```

Response message:
```
message PredictResponse {
    repeated PredictRequirements requirements = 1;
    repeated PredictFlavor flavors = 2;
    repeated PredictHostAggregate host_aggregates = 3;
}
```

Additional messages:
```
message PredictRequirements {
    double cpu_threads = 1;
    double disk_iops = 2;
    double network_bandwidth = 3;
    double ram_size = 4;
}

message PredictFlavor {
    uint32 disk = 1;
    uint32 ram = 2;
    uint32 vcpus = 3;
    string name = 4;
}

message PredictHostAggregateCPU {
    uint32 performance = 1;
    uint32 threads = 2;
}

message PredictHostAggregateDisk {
    uint32 iops = 1;
    uint32 size = 2;
}

message PredictHostAggregateRAM {
    uint32 bandwidth = 1;
    uint32 size = 2;
}

message PredictHostAggregate {
    PredictHostAggregateCPU cpu = 1;
    PredictHostAggregateDisk disk = 2;
    PredictHostAggregateRAM ram = 3;
}

```

#### RefreshClassifier
Refreshes all classifier neural networks with data from db.

#### RefreshPredictor
Refreshes all predictor neural networks with data from db.

#### WorkloadsCategories
Returns all workload categories.

Response message:
```
message WorkloadsCategoriesResponse {
    repeated WorkloadCategory workloads_categories = 1;
}
```

Additional messages:
```
message WorkloadCategory{
    string name = 1;
    repeated string parameters = 2;
}
```

#### ImportMetricsFromSwanExperiment
Imports all metrics from swan experiment to KRICO db.

Request message:
```
message ImportMetricsFromSwanExperimentRequest {
    string experiment_id=1;
}
```

#### ImportSamplesFromSwanExperiment
Imports monitor samples from swan experiment to KRICO db.

Request message:
```
message ImportSamplesFromSwanExperimentRequest {
    string experiment_id=1;
}
```

### KRICO installation
##### Requirements:
* Python 2.7
* [Pipenv](https://github.com/pypa/pipenv)

##### Installation and running
Edit existing config file (```experiments/krico/config.yml```), put your information about database and api.

```bash
database:
    host: your host
    port: your port
    keyspace: krico
    replication_factor: 1

api:
    host: your ip
    port: 5000
```

Go to experiment folder. Install virtual environment and run KRICO service.

```bash
cd experiments/krico/
pipenv install
pipenv run python main.py -c config.yml
```

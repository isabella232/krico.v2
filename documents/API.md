# KRICO REST API

KRICO module exposes REST API

## POST /api/v0.2/krico/launch

Call to launch new VM using KRICO module. User must define parameters of new instance (workload class, workload params, etc.)

### Request:

```json
launch_workload.json
{
	"image": "ubuntu trusty",
	"name": "instance-name",
	"host_aggregate": "krico.haswell",
	"network": "kriconet",
	"category": "bigdata",
	"parameters": {
		"data": 32,
		"processors": 24,
		"memory": 32
	},
	"user": "krico",
	"password": "krico",
	"tenant": "krico"
}
```

## POST /api/v0.2/krico/terminate

Call to terminate running VM using KRICO module. User must define VM instance ID.

### Request

```json
terminate_workload.json
{
	"instance_id": "phase-3-bigdata-hadoop-00026"
}
```

## POST /api/v0.2/krico/classify

Call to classify workload running on instance

### Request

```json
classify_workload.json
{
	"instance_id": "phase-3-bigdata-hadoop-00026"
}
```

## POST /api/v0.2/krico/predict-load

Call to predict load based on workload parameters, and create OpenStack flavor

### Request

```json
predict_load.json
{
    "category": "webserving",
    "image": "wrkld-webserving",
    "parameters": {
        "clients": 1000.0,
        "disk": 0.0
    }
}
```

### Response

{
  "predictions": [
    {
      "availability_zone": "nova",
      "configuration_id": "krico-cpu-8-10-ram-16-10-disk-900-500",
      "flavor": {
        "disk": 0,
        "name": "krico-3c-12m-0d",
        "ram": 12288,
        "vcpus": 3
      },
      "name": "krico-cpu-8-10-ram-16-10-disk-900-500",
      "requirements": {
        "cpu_threads": 2.674931085399587,
        "disk_iops": 90.20137739396459,
        "network_bandwidth": 1.0217705883780446,
        "ram_size": 11.538762950520601
      }
    },
    {
      "availability_zone": "nova",
      "configuration_id": "krico-cpu-8-10-ram-16-10-disk-4100-400",
      "flavor": {
        "disk": 0,
        "name": "krico-3c-12m-0d",
        "ram": 12288,
        "vcpus": 3
      },
      "name": "krico-cpu-8-10-ram-16-10-disk-4100-400",
      "requirements": {
        "cpu_threads": 2.8924004173285534,
        "disk_iops": 90.20137739396459,
        "network_bandwidth": 1.0217705883780446,
        "ram_size": 11.538762950520601
      }
    }
  ]
}


## GET /api/v0.2/krico/instances

Call to list all details about VMs running on OpenStack and started via KRICO module

### Response

```json
{
  "5b480bb8-5acd-4adb-a3bc-ae427d2b352f": {
    "availability_zone": {
      "configuration_id": "krico-cpu-48-10-ram-64-40-disk-1800-400",
      "cpu": {
        "performance": 10.0632589403,
        "threads": 48
      },
      "disk": {
        "iops": 387.142857143,
        "size": 1779.53691101
      },
      "name": "nova",
      "priority": 1.0,
      "ram": {
        "bandwidth": 38.0573521205,
        "size": 64.0
      }
    },
    "category": "webserving",
    "flavor": {
      "disk": 20,
      "name": "krico-3c-12m-20d",
      "ram": 12288,
      "vcpus": 3
    },
    "host": "node-45.domain.tld",
    "image": "wrkld-webserving-jmeter",
    "metrics": {
      "cpu:cache:misses": 175222.57643167066,
      "cpu:cache:references": 1136695.5094360397,
      "cpu:time": 0.00260959474493914,
      "disk:bandwidth:read": 0.0,
      "disk:bandwidth:write": 0.0,
      "disk:operations:read": 0.0,
      "disk:operations:write": 0.0,
      "network:bandwidth:receive": 4.924277450802601e-05,
      "network:bandwidth:send": 0.0,
      "network:packets:receive": 0.8005394034500447,
      "network:packets:send": 0.0,
      "ram:used": 0.7636756896972656
    },
    "name": "AUTOMATED-IMAGE-NAME",
    "parameters": {
      "clients": 100.0,
      "disk": 20.0
    },
    "requirements": {
      "cpu_threads": 2.9600368974854603,
      "disk_iops": 107.80631442246106,
      "network_bandwidth": 0.4295515395059756,
      "ram_size": 11.715953287209285
    },
    "start_time": "Thu, 25 Aug 2016 15:16:55 GMT",
    "state": "running"
  },
  "61f435ee-920e-4a67-bbe3-40362ae920e9": {
    "availability_zone": {
      "configuration_id": "krico-cpu-48-10-ram-64-40-disk-1800-400",
      "cpu": {
        "performance": 10.0632589403,
        "threads": 48
      },
      "disk": {
        "iops": 387.142857143,
        "size": 1779.53691101
      },
      "name": "nova",
      "priority": 1.0,
      "ram": {
        "bandwidth": 38.0573521205,
        "size": 64.0
      }
    },
    "category": "unknown",
    "flavor": {
      "disk": 20,
      "name": "krico-4.0c-16.0m-20d",
      "ram": 16384.0,
      "vcpus": 4.0
    },
    "host": "node-23.domain.tld",
    "image": "wrkld-science-hpcg",
    "metrics": {
      "cpu:cache:misses": 57767.57246789746,
      "cpu:cache:references": 1177747.745694235,
      "cpu:time": 0.009783225939871128,
      "disk:bandwidth:read": 0.0,
      "disk:bandwidth:write": 0.0,
      "disk:operations:read": 0.0,
      "disk:operations:write": 0.0,
      "network:bandwidth:receive": 7.55310964966908e-05,
      "network:bandwidth:send": 6.523140151986933e-05,
      "network:packets:receive": 0.200000240000288,
      "network:packets:send": 0.200000240000288,
      "ram:used": 0.4979248046875
    },
    "name": "AUTOMATED-IMAGE-NAME",
    "parameters": {
      "disk": 20.0,
      "ram": 16384.0,
      "vcpus": 4.0
    },
    "start_time": "Fri, 26 Aug 2016 07:46:33 GMT",
    "state": "running"
  }
}
```

## GET /api/v0.2/krico/workloads

Call to list all information about workloads configuration

### Response

```json
{
  "categories": [
    {
      "name": "bigdata",
      "parameters": [
        "processors",
        "memory",
        "data"
      ]
    },
    {
      "name": "caching",
      "parameters": [
        "memory",
        "ratio",
        "clients"
      ]
    },
    {
      "name": "oltp",
      "parameters": [
        "data",
        "clients"
      ]
    },
    {
      "name": "science",
      "parameters": [
        "processors",
        "memory"
      ]
    },
    {
      "name": "streaming",
      "parameters": [
        "bitrate",
        "clients"
      ]
    },
    {
      "name": "webserving",
      "parameters": [
        "clients"
      ]
    }
  ]
}
```

## POST /api/v0.2/krico/refresh-classifier

Method to retrain classifier neural network using new metrics, collected with KRICO

## POST /api/v0.2/krico/refresh-predictor

Method to retrain predictor neural network using new metrics, collected with KRICO

## POST /api/v0.2/krico/refresh-instances

Method to refresh VM instances data using filtered and averaged samples of the instance metrics collected with KRICO

# **KRICO and OpenStack integration plan**

Integration possibilities:

1. [OpenStack UI extension] (#openstack-ui-extension)
    * [VM launcher basic on user parameters] (#vm-launcher-basic-on-user-parameters)
    * [Flavor creation assistant] (#flavor-creation-assistant)
    * [Classification assistant] (#classification-assistant)
2. [VM Scheduler] (#vm-scheduler)
3. [Normalized Compute Units] (#normalized-compute-units)
4. [Watcher] (#watcher)

## OpenStack UI extension
OpenStack UI - Horizon is the best place to initial integration with KRICO module. It provides set of functionalities to launch VMs, and administrate them.
It is based on Django framework, and built on top of REST API.
Adding new dashboard do not need to patching existing code. It is only addition of new panels.

### VM launcher basic on user parameters
Main functionality of KRICO in terms of integration with Horizon is launching VMs with simply user parameters.
It will be built on top of POST /krico/v0.1/launch call. Launcher consists of view which enables user to choose workload class, and pass specific parameters.
Basic on it KRICO module will estimate how many resources is needed, and create new flavor if there is no other one with specified amount of resources.
In next step VM will start automatically using newly created (or chosen one) flavor.

### Flavor creation assistant
It enables to create flavors basic on usage parameters, and workload class. Panel will be build on top of POST /krico/v0.1/predict-load call.
Basic on parameters, and class KRICO will estimate how many resource is needed for specific workload. It will also provide some metadata to flavor (like workload class)

Issues that impacts this functionality: [#32] (https://github.com/intelsdi-x/krico/issues/32)

### Classification assistant
This panel enables classification of each VM running on OpenStack environment. Like the other ones it is built on top of POST /krico/v0.1/classify.
Current implementation of KRICO is not enabling full functionality for complete this panel. There is no possibility to "live" classification of VM, and also user is not able to classify VM not launched using KRICO.

Related issues: [#33](https://github.com/intelsdi-x/krico/issues/33), [#9](https://github.com/intelsdi-x/krico/issues/9)

## VM Scheduler
Other place to possible integration between KRICO and OpenStack is scheduler. It can be realized by scheduler hints sending with request to launch VM.
The hint can provide server to run VM on it.
This way of integration needs to provide patches for original OpenStack code.

## Normalized Compute Units
TBD

## Watcher
TBD

# Flavor creation

KRICO module should create flavor based on workloads user parameters.

## Flavor creation during VM launch

Basic functionality of KRICO module is to launch instance with resource allocated using user parameters.
Based on prediction proper flavor should be created (even if environment is heterogenic).
Module is able to estimate parameters such like:
<ul>
    <li>VCPU needed</li>
    <li>RAM allocation</li>
    <li>Storage IO Limit</li>
    <li>Network IO Limit</li>
</ul>
Storage and Network parameters are configurable with using flavor property feature. It is mapping between limits set in flavor metadata, and cgroup created for launched VM.
In first implementation flavor creation will base only on VCPUs, and RAM allocation.

### Flavor creation workflow

Request is sent by user with workload class, and parameters passed for VM. KRICO module estimates resources which should be allocated.
Based on prediction module send request to create flavor. Using this newly created flavor VM is spawning.
After VM spawn flavor should be deleted. In this case flavors aren't reusable.

## Flavor creation based on predict load

Idea, and workflow are basically the same as in creation during launch. But there are some differences.
First difference is that flavor aren't deleted after VM spawn, and they are reusable. Also there is not only one flavor created, but a bunch of them.
One flavor per host aggregate (per architecture) to enable support for heterogenity. 
Resource allocation are based on prediction for reference architecture, and multiplied with aggregate parameter.

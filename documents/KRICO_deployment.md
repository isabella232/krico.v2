# KRICO deployment for existing OpenStack environment

Ideal environment to deploy KRICO module is clean OpenStack installation without host aggregates, and VMs running on hosts.
All components could be run also on bare metal host.

## Prerequisites

For installation on either clean, and production environment those user should prepare:
<ul>
    <li>Dedicated server for all VMs (Installer, API, Database)</li>
    <li>Host should be accessible for installer to deploy monitoring agents on them</li>
</ul>

## Installation process

TBD

## Configuration

After KRICO VMs are running, and monitors are deployed on hosts new host aggregates will be created.
Each aggregate is based on CPU architecture (one aggregate per unique CPU Arch). It is needed to support heterogenity of cloud environment.
Information about unique CPU architectures are accessible from OpenStack Compute API.

*Note*

```
To specify heterogenity factor there should be at least one idle host per each aggregate to run benchmark on it
```

Additional dashboard for OpenStack UI will be installed automatically. Using dashboard user can specify some metadata for VM images.
There should be added information about workload class which is served by specific image.

_default_cpu_divisor = 10.0


def normalize(requirements, hardware_info):
    requirements_normalized = requirements.copy()
    requirements_normalized.cpu_threads *= hardware_info.cpu.performance / _default_cpu_divisor
    return requirements_normalized


def denormalize(requirements, hardware_info):
    requirements_denormalized = requirements.copy()
    requirements_denormalized.cpu_threads /= hardware_info.cpu.performance / _default_cpu_divisor
    return requirements_denormalized

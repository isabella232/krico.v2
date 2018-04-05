__author__ = 'pmatyjas'


def validate_parameters(parameters_to_validate, expected_parameters=[], *args):
    if parameters_to_validate != {}:
        if len(parameters_to_validate.keys()) == len(expected_parameters):
            for param in parameters_to_validate.keys():
                if param in expected_parameters:
                    continue
                else:
                    return False
            return True
        return False
    return False


def verify_load(load_predicted):
    if load_predicted['vcpus'] < 0:
        return False
    if load_predicted['ram'] < 0:
        return False
    if load_predicted['disk_io'] < 0:
        return False
    if load_predicted['net_io'] < 0:
        return False
    return True

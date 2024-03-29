import json
import os
import uuid
import database


class TestFillDatabase(object):

    def test_fill_database(self):
        classifier_data_path = \
            '{}/test_classifier_data.json'.\
            format(os.path.dirname(os.path.abspath(__file__)))
        predictor_data_path = \
            '{}/test_predictor_data.json'.\
            format(os.path.dirname(os.path.abspath(__file__)))
        database.fill(classifier_data_path, predictor_data_path)

        with open(classifier_data_path) as f:
            data = json.load(f)

        for expected in data:
            db_object = database.ClassifierInstance.filter(
                id=uuid.UUID(expected['id'])).allow_filtering().first()
            assert db_object.category == expected['category']
            assert db_object.name == expected['name']
            assert db_object.configuration_id == expected['host_aggregate'][
                'configuration_id']
            assert db_object.parameters == expected['parameters']
            assert db_object.host_aggregate.disk == expected['host_aggregate'][
                'disk']
            assert db_object.host_aggregate.ram == expected['host_aggregate'][
                'ram']
            assert db_object.host_aggregate.name == expected['host_aggregate'][
                'name']
            assert db_object.host_aggregate.configuration_id == expected[
                'host_aggregate']['configuration_id']
            assert db_object.host_aggregate.cpu == expected['host_aggregate'][
                'cpu']
            assert db_object.flavor.vcpus == expected['flavor']['vcpus']
            assert db_object.flavor.disk == expected['flavor']['disk']
            assert db_object.flavor.ram == expected['flavor']['ram']
            assert db_object.flavor.name == expected['flavor']['name']
            assert db_object.image == expected['image']
            assert db_object.host == expected['host']
            assert db_object.instance_id == expected['instance_id']
            assert db_object.resource_usage == expected['load_measured']

            db_object = database.HostAggregate.filter(
                name=expected['host_aggregate'][
                    'name']).allow_filtering().first()
            assert db_object.disk == expected['host_aggregate']['disk']
            assert db_object.ram == expected['host_aggregate']['ram']
            assert db_object.name == expected['host_aggregate']['name']
            assert db_object.configuration_id == expected['host_aggregate'][
                'configuration_id']
            assert db_object.cpu == expected['host_aggregate']['cpu']

        with open(predictor_data_path) as f:
            data = json.load(f)

        for expected in data:
            db_object = database.PredictorInstance.filter(
                id=uuid.UUID(expected['id'])).allow_filtering().first()
            assert db_object.instance_id == expected['instance_id']
            assert db_object.image == expected['image']
            assert db_object.category == expected['category']
            assert db_object.requirements == expected['requirements']
            assert db_object.parameters == expected['parameters']

            db_object = database.Image.filter(
                image=expected['image']).allow_filtering().first()
            assert db_object.image == expected['image']
            assert db_object.category == expected['category']

        database.delete_database()

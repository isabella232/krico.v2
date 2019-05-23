import os

import mock

import analysis.classifier

configuration_id = 'configuration_id'


class TestEnoughSamples(object):

    @mock.patch('krico.analysis.classifier.ClassifierInstance')
    def test_if_not_enough_samples(self, mock_classifier_instance):
        mock_classifier_instance.objects.filter.return_value.\
            allow_filtering.return_value.count.return_value = 0
        assert analysis.classifier._enough_samples(
            'category', 'configuration_id') is False

    @mock.patch('krico.analysis.classifier.ClassifierInstance')
    def test_if_enough_samples(self, mock_classifier_instance):
        mock_classifier_instance.objects.filter.return_value.\
            allow_filtering.return_value.count.return_value = 80
        assert analysis.classifier._enough_samples(
            'category', 'configuration_id') is True


class TestClassifier(object):

    def test_if_model_is_created_after_object_initialization(self):
        assert hasattr(analysis.classifier.
                       _Classifier(configuration_id), 'model')

    def test_if_model_is_compiled_after_object_initialization(self):
        assert analysis.classifier.\
                   _Classifier(configuration_id).model.built is True

    def test_if_classifier_have_configuration_id(self):
        assert analysis.classifier.\
                   _Classifier(configuration_id).\
                   configuration_id == configuration_id

    def test_if_classifier_have_x_maxima(self):
        assert hasattr(analysis.classifier.
                       _Classifier(configuration_id), 'x_maxima')


class TestGetClassifier(object):

    @mock.patch('krico.analysis.classifier.ClassifierNetwork')
    def test_if_return_specific_network(self, mock_classifier_network):

        classifier_row = analysis.classifier.ClassifierNetwork
        classifier_row.configuration_id = configuration_id

        classifier = analysis.classifier._Classifier(configuration_id)
        h5fd_file_name = 'model_{}.h5'.format(configuration_id)

        classifier.model.save(h5fd_file_name)

        with open(h5fd_file_name, mode='rb') as f:
            classifier_row.model = f.read()
            f.close()
        os.remove(h5fd_file_name)

        mock_classifier_network.objects.filter.return_value.get.return_value =\
            classifier_row

        test_classifier = \
            analysis.classifier._get_classifier(configuration_id)

        assert test_classifier.model.metrics_names ==\
            classifier.model.metrics_names
        assert test_classifier.configuration_id == classifier.configuration_id

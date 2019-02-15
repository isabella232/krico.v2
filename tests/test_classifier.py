import mock
import krico.analysis.classifier


@mock.patch.dict(krico.analysis.classifier.config,
                 {'minimal_samples': 40})
class TestEnoughSamples(object):

    @mock.patch('krico.database.ClassifierInstance')
    def test_if_not_enough_samples(self, mock_classifier_instance):
        mock_classifier_instance.objects.filter.return_value.\
            allow_filtering.return_value.count.return_value = 0
        assert krico.analysis.classifier._enough_samples(
            'configuration_id') is False

    @mock.patch('krico.database.ClassifierInstance')
    def test_if_enough_samples(self, mock_classifier_instance):
        mock_classifier_instance.objects.filter.return_value.\
            allow_filtering.return_value.count.return_value = 80
        assert krico.analysis.classifier._enough_samples(
            'configuration_id') is True


class TestClassifier(object):

    def test_if_model_is_correct(self):
        classifier = krico.analysis.classifier._Classifier('configuration_id')

        assert classifier.model
        assert classifier.model.built is True
        assert classifier.configuration_id is "configuration_id"
        assert isinstance(classifier.x_maxima, list)
        assert len(classifier.model.layers) == 3

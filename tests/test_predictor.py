import mock
import pickle

import krico.analysis.predictor

from krico import core

category = 'bigdata'
image = 'krico-img'


class TestEnoughSamples(object):

    @mock.patch('krico.analysis.predictor.PredictorInstance')
    def test_if_not_enough_samples(self, mock_predictor_instance):
        mock_predictor_instance.objects.filter.return_value.\
            allow_filtering.return_value.count.return_value = 0
        assert krico.analysis.predictor._enough_samples(category) is False
        assert krico.analysis.predictor._enough_samples(category,
                                                        image) is False

    @mock.patch('krico.analysis.predictor.PredictorInstance')
    def test_if_enough_samples(self, mock_predictor_instance):
        mock_predictor_instance.objects.filter.return_value.\
            allow_filtering.return_value.count.return_value = \
            core.configuration['predictor']['minimal_samples']
        assert krico.analysis.predictor._enough_samples(category) is True
        assert krico.analysis.predictor._enough_samples(category,
                                                        image) is True


class TestPredictor(object):

    def test_if_model_is_created_after_object_initialization(self):
        assert krico.analysis.predictor._Predictor(category, image).model

    def test_if_model_is_compiled_after_object_initialization(self):
        assert krico.analysis.predictor._Predictor(category,
                                                   image).model.built is True

    def test_if_predictor_have_image_name(self):
        assert krico.analysis.predictor._Predictor(category,
                                                   image).image == image

    def test_if_predictor_have_category_name(self):
        assert krico.analysis.predictor._Predictor(category,
                                                   image).category == category

    def test_if_predictor_have_x_maxima(self):
        assert krico.analysis.predictor._Predictor(category,
                                                   image).x_maxima == []


class TestGetPredictor(object):

    @mock.patch('krico.analysis.predictor.PredictorNetwork')
    def test_if_return_specific_image_network(self, mock_predictor_network):

        predictor = krico.analysis.predictor.PredictorNetwork
        predictor.image = image
        predictor.category = category
        predictor.network = pickle.dumps(
            krico.analysis.predictor._Predictor(category, image))

        mock_predictor_network.objects.filter.return_value.\
            allow_filtering.return_value.first.return_value = \
            predictor

        assert isinstance(
            krico.analysis.predictor._get_predictor(category, image),
            krico.analysis.predictor._Predictor)

    @mock.patch('krico.analysis.predictor._create_predictor')
    @mock.patch('krico.analysis.predictor._enough_samples')
    @mock.patch('krico.analysis.predictor.PredictorNetwork')
    def test_if_create_specific_image_network(self, mock_predictor_network,
                                              mock_enough_samples,
                                              mock_create_predictor):
        mock_predictor_network.objects.filter.return_value.\
            allow_filtering.return_value.first.return_value = None

        mock_enough_samples.return_value = True

        mock_create_predictor.return_value = krico.\
            analysis.predictor._Predictor(category, image)

        assert isinstance(
            krico.analysis.predictor._get_predictor(category, image),
            krico.analysis.predictor._Predictor)

    @mock.patch('krico.analysis.predictor._enough_samples')
    @mock.patch('krico.analysis.predictor.PredictorNetwork')
    def test_if_return_category_network(self, mock_predictor_network,
                                        mock_enough_samples):

        predictor = krico.analysis.predictor.PredictorNetwork
        predictor.image = image
        predictor.category = category
        predictor.network = pickle.dumps(
            krico.analysis.predictor._Predictor(category, image))

        mock_predictor_network.objects.filter.return_value.\
            allow_filtering.return_value.first.side_effect = \
            [None, predictor]

        mock_enough_samples.return_value = False

        assert isinstance(
            krico.analysis.predictor._get_predictor(category, image),
            krico.analysis.predictor._Predictor)

    @mock.patch('krico.analysis.predictor._create_predictor')
    @mock.patch('krico.analysis.predictor._enough_samples')
    @mock.patch('krico.analysis.predictor.PredictorNetwork')
    def test_if_create_category_network(self, mock_predictor_network,
                                        mock_enough_samples,
                                        mock_create_predictor):
        mock_predictor_network.objects.filter.return_value.allow_filtering.\
            return_value.first.return_value = None

        mock_enough_samples.side_effect = [False, True]

        mock_create_predictor.return_value = \
            krico.analysis.predictor._Predictor(category, image)

        assert isinstance(
            krico.analysis.predictor._get_predictor(category, image),
            krico.analysis.predictor._Predictor)

    @mock.patch('krico.analysis.predictor._enough_samples')
    @mock.patch('krico.analysis.predictor.PredictorNetwork')
    def test_if_raise_exception(self, mock_predictor_network,
                                mock_enough_samples):
        mock_predictor_network.objects.filter.return_value.\
            allow_filtering.return_value.first.return_value = None
        mock_enough_samples.return_value = False

        try:
            krico.analysis.predictor._get_predictor(category, image)
        except Exception as e:
            assert isinstance(e, krico.core.exception.NotEnoughResourcesError)

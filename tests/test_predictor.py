import os

import mock

import analysis.predictor

import core

category = 'bigdata'
image = 'krico-img'


class TestEnoughSamples(object):

    @mock.patch('krico.analysis.predictor.PredictorInstance')
    def test_if_not_enough_samples(self, mock_predictor_instance):
        mock_predictor_instance.objects.filter.return_value.\
            allow_filtering.return_value.count.return_value = 0
        assert analysis.predictor._enough_samples(category) is False
        assert analysis.predictor._enough_samples(category,
                                                  image) is False

    @mock.patch('krico.analysis.predictor.PredictorInstance')
    def test_if_enough_samples(self, mock_predictor_instance):
        mock_predictor_instance.objects.filter.return_value.\
            allow_filtering.return_value.count.return_value = \
            core.configuration['predictor']['minimal_samples']
        assert analysis.predictor._enough_samples(category) is True
        assert analysis.predictor._enough_samples(category,
                                                  image) is True


class TestPredictor(object):

    def test_if_model_is_created_after_object_initialization(self):
        assert hasattr(analysis.predictor.
                       _Predictor(category, image), 'model')

    def test_if_model_is_compiled_after_object_initialization(self):
        assert analysis.predictor._Predictor(category,
                                             image).model.built is True

    def test_if_predictor_have_image_name(self):
        assert analysis.predictor._Predictor(category,
                                             image).image == image

    def test_if_predictor_have_category_name(self):
        assert analysis.predictor._Predictor(category,
                                             image).category == category

    def test_if_predictor_have_x_maxima(self):
        assert hasattr(
            analysis.predictor._Predictor(category, image), 'x_maxima')

    def test_if_predictor_have_y_maxima(self):
        assert hasattr(
            analysis.predictor._Predictor(category, image), 'y_maxima')


class TestGetPredictor(object):

    @mock.patch('krico.analysis.predictor.PredictorNetwork')
    def test_if_return_specific_image_network(self, mock_predictor_network):

        predictor_row = analysis.predictor.PredictorNetwork
        predictor_row.image = image
        predictor_row.category = category

        predictor = analysis.predictor._Predictor(category, image)
        h5fd_file_name = 'model_{}_{}.h5'.format(category, image)

        predictor.model.save(h5fd_file_name)

        with open(h5fd_file_name, mode='rb') as f:
            predictor_row.model = f.read()
            f.close()
        os.remove(h5fd_file_name)

        mock_predictor_network.objects.filter.return_value.get.return_value = \
            predictor_row

        test_predictor = \
            analysis.predictor._get_predictor(category, image)

        assert test_predictor.image == predictor_row.image
        assert test_predictor.category == predictor_row.category
        assert test_predictor.model.metrics_names ==\
            predictor.model.metrics_names

    @mock.patch('krico.analysis.predictor._create_predictor')
    @mock.patch('krico.analysis.predictor._enough_samples')
    @mock.patch('krico.analysis.predictor.PredictorNetwork')
    def test_if_create_specific_image_network(self, mock_predictor_network,
                                              mock_enough_samples,
                                              mock_create_predictor):
        mock_predictor_network.objects.filter.return_value.\
            get.return_value = None

        mock_enough_samples.return_value = True

        mock_create_predictor.return_value = analysis.predictor._Predictor(category, image)

        assert isinstance(
            analysis.predictor._get_predictor(category, image),
            analysis.predictor._Predictor)

    @mock.patch('krico.analysis.predictor._enough_samples')
    @mock.patch('krico.analysis.predictor.PredictorNetwork')
    def test_if_return_category_network(self, mock_predictor_network,
                                        mock_enough_samples):

        predictor_row = analysis.predictor.PredictorNetwork
        predictor_row.image = image
        predictor_row.category = category

        predictor = analysis.predictor._Predictor(category, image)
        h5fd_file_name = 'model_{}_{}.h5'.format(category, image)

        predictor.model.save(h5fd_file_name)

        with open(h5fd_file_name, mode='rb') as f:
            predictor_row.model = f.read()
            f.close()
        os.remove(h5fd_file_name)

        mock_predictor_network.objects.filter.return_value.\
            get.side_effect = \
            [None, predictor_row]

        mock_enough_samples.return_value = False

        test_predictor = \
            analysis.predictor._get_predictor(category, image)

        assert test_predictor.image == predictor_row.image
        assert test_predictor.category == predictor_row.category
        assert test_predictor.model.metrics_names ==\
            predictor.model.metrics_names

    @mock.patch('krico.analysis.predictor._create_predictor')
    @mock.patch('krico.analysis.predictor._enough_samples')
    @mock.patch('krico.analysis.predictor.PredictorNetwork')
    def test_if_create_category_network(self, mock_predictor_network,
                                        mock_enough_samples,
                                        mock_create_predictor):
        mock_predictor_network.objects.filter.return_value.get.return_value =\
            None

        mock_enough_samples.side_effect = [False, True]

        mock_create_predictor.return_value = \
            analysis.predictor._Predictor(category, image)

        assert isinstance(
            analysis.predictor._get_predictor(category, image),
            analysis.predictor._Predictor)

    @mock.patch('krico.analysis.predictor._enough_samples')
    @mock.patch('krico.analysis.predictor.PredictorNetwork')
    def test_if_raise_exception(self, mock_predictor_network,
                                mock_enough_samples):
        mock_predictor_network.objects.filter.return_value.get.return_value =\
            None
        mock_enough_samples.return_value = False

        try:
            analysis.predictor._get_predictor(category, image)
        except Exception as e:
            assert isinstance(e, krico.core.exception.NotEnoughResourcesError)

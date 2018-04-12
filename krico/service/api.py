import multiprocessing

import flask
import flask_classy

import krico.core.configuration
import krico.core.logger
import krico.core.executable.daemon

import krico.analysis.classifier
import krico.analysis.predictor.refresh

import krico.service.classifier
import krico.service.predictor
import krico.service.dataprovider

_logger = krico.core.logger.get(__name__)
_configuration = krico.core.configuration.root


class KricoView(flask_classy.FlaskView):
    def _request(self, api_func, *args, **kwargs):
        response = {}
        try:
            api_func(*args, **kwargs)
        except Exception as ex:
            return flask.jsonify({
                'error': 'Internal Server Error: {}'.format(ex)
            }), 500
        return flask.jsonify(response), 201

    @flask_classy.route('/predict-load', methods=['POST'])
    def predict_load(self):
        return krico.service.predictor.predict_load_request()

    @flask_classy.route('/classify', methods=['POST'])
    def classify(self):
        return krico.service.classifier.classify()

    @flask_classy.route('/workloads', methods=['GET'])
    def get_all_workloads(self):
        return krico.service.dataprovider.get_all_workloads()

    @flask_classy.route('/refresh-classifier', methods=['POST'])
    def refresh_classifier(self):
        return self._request(krico.analysis.classifier.refresh)

    @flask_classy.route('/refresh-predictor', methods=['POST'])
    def refresh_predictor(self):
        return self._request(krico.analysis.predictor.refresh.run)


class RestApiWorker(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        _logger.info('Initializing RestApiWorker.')

        self.__rest = flask.Flask('KRICO API Service')
        self.__rest.register_error_handler(404, self.not_found)

        KricoView.register(
            self.__rest,
            route_base='krico/v{}'.format(_configuration.service.api.version)
        )

        for rule in self.__rest.url_map.iter_rules():
            if RestApiWorker.has_no_empty_params(rule):
                url = rule.rule
                _logger.info('{} - {}'.format(url, rule.endpoint))

    @staticmethod
    def has_no_empty_params(rule):
        defaults = rule.defaults if rule.defaults is not None else ()
        arguments = rule.arguments if rule.arguments is not None else ()
        return len(defaults) >= len(arguments)

    def run(self):
        try:
            self.__rest.run(
                debug=False,
                host=_configuration.service.api.host,
                port=_configuration.service.api.port,
                use_reloader=False,
                threaded=False,
                processes=10
            )
        except Exception as e:
            _logger.error('Exception during run.')
            _logger.error(e)

        except:
            _logger.error('Unknown exception.')
            raise

        finally:
            _logger.info('REST API shutdown.')

    @staticmethod
    def not_found(error):
        return flask.make_response(flask.jsonify({'error': str(error)}), 404)

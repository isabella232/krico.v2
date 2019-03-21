import pytest

from krico.analysis.converter import\
    prepare_prediction_for_host_aggregate, prepare_mean_sample, _filter_peaks

from krico.core.exception import NotEnoughResourcesError


class TestPreparePredictionForHostAggregate(object):

    def test_raises_exception_on_not_implemented_allocation_mode(self):
        with pytest.raises(NotImplementedError):
            prepare_prediction_for_host_aggregate(
                aggregate=dict({'cpu': {'threads': 100}, 'ram': {'size': 100},
                                'disk': {'size': 100}}),
                requirements=dict(
                    {'cpu_threads': 10, 'ram_size': 10, 'disk': 10}),
                allocation=""
            )

    @pytest.mark.parametrize("aggregate,requirements", (
            (dict({'cpu': {'threads': 100}, 'ram': {'size': 100},
                   'disk': {'size': 100}, 'configuration_id': 'test'}),
             dict({'cpu_threads': 200, 'ram_size': 10, 'disk': 10})),
            (dict({'cpu': {'threads': 100}, 'ram': {'size': 100},
                   'disk': {'size': 100}, 'configuration_id': 'test'}),
             dict({'cpu_threads': 10, 'ram_size': 200, 'disk': 10})),
            (dict({'cpu': {'threads': 100}, 'ram': {'size': 100},
                   'disk': {'size': 100}, 'configuration_id': 'test'}),
             dict({'cpu_threads': 10, 'ram_size': 10, 'disk': 200}))
    ))
    def test_raises_exception_on_not_enough_resources(self, aggregate,
                                                      requirements):
        with pytest.raises(NotEnoughResourcesError):
            prepare_prediction_for_host_aggregate(
                aggregate, requirements, 'shared')

    @pytest.mark.parametrize("aggregate,requirements,expected", [
        (dict({'cpu': {'threads': 100}, 'ram': {'size': 100},
               'disk': {'size': 100}}),
         dict({'cpu_threads': 10, 'ram_size': 10, 'disk': 10}),
         dict({'vcpus': 100, 'ram': 90, 'disk': 45})),
        (dict({'cpu': {'threads': 21.10}, 'ram': {'size': 21.10},
               'disk': {'size': 21.10}}),
         dict({'cpu_threads': 10, 'ram_size': 10, 'disk': 10}),
         dict({'vcpus': 21, 'ram': 18, 'disk': 9}))
    ])
    def test_give_max_values_if_allocation_mode_is_set_as_exclusive(
            self, aggregate, requirements, expected):
        prediction =\
            prepare_prediction_for_host_aggregate(
                aggregate, requirements, 'exclusive')
        assert prediction['flavor']['vcpus'] == expected['vcpus']
        assert prediction['flavor']['ram'] == expected['ram']
        assert prediction['flavor']['disk'] == expected['disk']

    @pytest.mark.parametrize("aggregate,requirements,expected", [
        (dict({'cpu': {'threads': 100}, 'ram': {'size': 100},
               'disk': {'size': 100}}),
         dict({'cpu_threads': 10, 'ram_size': 10, 'disk': 10}),
         dict({'vcpus': 10, 'ram': 10, 'disk': 10}))
    ])
    def test_set_shared_mode_if_none_allocation_is_provided(
            self, aggregate, requirements, expected):
        prediction =\
            prepare_prediction_for_host_aggregate(
                aggregate, requirements)
        assert prediction['flavor']['vcpus'] == expected['vcpus']
        assert prediction['flavor']['ram'] == expected['ram']
        assert prediction['flavor']['disk'] == expected['disk']


class TestPrepareMeanSamples(object):
    @pytest.mark.parametrize("samples,metrics,expected", [
        ([
             {
                 u'network:bandwidth:send': 1.887127763386713e-05,
                 u'network:packets:send': 0.20003221875686217,
                 u'network:bandwidth:receive': 5.263757545701754e-05,
                 u'network:packets:receive': 0.7795452783119171,
                 u'disk:operations:write': 167.00452531121618,
                 u'cpu:cache:misses': 1240720.9662992768,
                 u'disk:operations:read': 0.19475434240244463,
                 u'disk:bandwidth:read': 0.0007607591500095493,
                 u'disk:bandwidth:write': 1.9625648529374706,
                 u'cpu:cache:references': 6110426.3023777725,
                 u'cpu:time': 1.4460558955283076,
                 u'ram:used': 8.803116333790314
             },
             {
                 u'network:bandwidth:send': 1.552961910823629e-05,
                 u'network:packets:send': 0.1772154248021715,
                 u'network:bandwidth:receive': 6.094802017788318e-05,
                 u'network:packets:receive': 0.7721110510696103,
                 u'disk:operations:write': 149.86158506649414,
                 u'cpu:cache:misses': 1551639.9522612363,
                 u'disk:operations:read': 2.357873514884857,
                 u'disk:bandwidth:read': 0.07396791527157995,
                 u'disk:bandwidth:write': 1.939923184380047,
                 u'cpu:cache:references': 8651662.880922629,
                 u'cpu:time': 1.4446881608011113,
                 u'ram:used': 8.246416303846571
             },
             {
                 u'network:bandwidth:send': 0.00014351059103579906,
                 u'network:packets:send': 0.626653603580777,
                 u'network:bandwidth:receive': 0.0001329149002294476,
                 u'network:packets:receive': 1.4577354320985585,
                 u'disk:operations:write': 162.54765926511172,
                 u'cpu:cache:misses': 1791682.7781733235,
                 u'disk:operations:read': 2.159686207583601,
                 u'disk:bandwidth:read': 0.06723961441771219,
                 u'disk:bandwidth:write': 2.256862742338856,
                 u'cpu:cache:references': 9026114.420051984,
                 u'cpu:time': 1.4690314594708642,
                 u'ram:used': 8.707352913750542
             },
             {
                 u'network:bandwidth:send': 1.5278649352025518e-05,
                 u'network:packets:send': 0.16500948338976276,
                 u'network:bandwidth:receive': 5.1379744918779076e-05,
                 u'network:packets:receive': 0.770007937847795,
                 u'disk:operations:write': 159.06891242789828,
                 u'cpu:cache:misses': 1700240.4030158173,
                 u'disk:operations:read': 2.0712552382609792,
                 u'disk:bandwidth:read': 0.061793020141751864,
                 u'disk:bandwidth:write': 2.286414942652157,
                 u'cpu:cache:references': 8385424.249579716,
                 u'cpu:time': 1.4302306012205936,
                 u'ram:used': 7.918641125714338
             },
             {
                 u'network:bandwidth:send': 12.200491924604377,
                 u'network:packets:send': 4446.299222391919,
                 u'network:bandwidth:receive': 12.557504984727101,
                 u'network:packets:receive': 10719.725360211278,
                 u'disk:operations:write': 50.859475994788575,
                 u'cpu:cache:misses': 9605447.669899432,
                 u'disk:operations:read': 104.58892194054663,
                 u'disk:bandwidth:read': 5.519096814037756,
                 u'disk:bandwidth:write': 17.37958631108488,
                 u'cpu:cache:references': 31455029.075490095,
                 u'cpu:time': 8.297991093080956,
                 u'ram:used': 62.54437361221558
             },
             {
                 u'network:bandwidth:send': 1.0624063964497887,
                 u'network:packets:send': 258.473660737988,
                 u'network:bandwidth:receive': 1.6808510029295298,
                 u'network:packets:receive': 1288.730560373094,
                 u'disk:operations:write': 15.072419553563046,
                 u'cpu:cache:misses': 15549640.083651531,
                 u'disk:operations:read': 185.35226377854576,
                 u'disk:bandwidth:read': 11.439677270073561,
                 u'disk:bandwidth:write': 1.7480721174904708,
                 u'cpu:cache:references': 45918986.87753086,
                 u'cpu:time': 11.038102142741344,
                 u'ram:used': 62.55275838883197
             },
             {
                 u'network:bandwidth:send': 1.7262400453529506e-05,
                 u'network:packets:send': 0.18778991057513741,
                 u'network:bandwidth:receive': 5.2022567001026125e-05,
                 u'network:packets:receive': 0.7804664737976675,
                 u'disk:operations:write': 174.55772521059401,
                 u'cpu:cache:misses': 1116610.189636474,
                 u'disk:operations:read': 2.3783666325822046,
                 u'disk:bandwidth:read': 0.07336057342298213,
                 u'disk:bandwidth:write': 1.733850669441367,
                 u'cpu:cache:references': 5915107.729142298,
                 u'cpu:time': 1.4526415087395796,
                 u'ram:used': 8.716318199433475
             },
             {
                 u'network:bandwidth:send': 8.045462036830106,
                 u'network:packets:send': 1841.4261287909187,
                 u'network:bandwidth:receive': 11.227087738055177,
                 u'network:packets:receive': 7288.909024141612,
                 u'disk:operations:write': 48.56230483860581,
                 u'cpu:cache:misses': 22574918.02245617,
                 u'disk:operations:read': 31.25893434781608,
                 u'disk:bandwidth:read': 2.1749542808893976,
                 u'disk:bandwidth:write': 17.946558935212927,
                 u'cpu:cache:references': 53939672.690121956,
                 u'cpu:time': 13.129862008708173,
                 u'ram:used': 60.94693231661719
             },
             {
                 u'network:bandwidth:send': 5.823458110305426,
                 u'network:packets:send': 2141.736265987585,
                 u'network:bandwidth:receive': 6.114483927147543,
                 u'network:packets:receive': 5421.00167191352,
                 u'disk:operations:write': 49.0819137774473,
                 u'cpu:cache:misses': 31743178.387397204,
                 u'disk:operations:read': 0.002152564452953821,
                 u'disk:bandwidth:read': 7.306234920070199e-06,
                 u'disk:bandwidth:write': 15.750522826120974,
                 u'cpu:cache:references': 63837010.07697736,
                 u'cpu:time': 11.049751331951562,
                 u'ram:used': 45.77971399084938
             },
             {
                 u'network:bandwidth:send': 1.5087172017661242e-05,
                 u'network:packets:send': 0.1636530710776753,
                 u'network:bandwidth:receive': 7.681921036172207e-05,
                 u'network:packets:receive': 1.2490147539983887,
                 u'disk:operations:write': 199.18371391711432,
                 u'cpu:cache:misses': 1938375.8848708628,
                 u'disk:operations:read': 0.3062232259370841,
                 u'disk:bandwidth:read': 0.0023194300252082044,
                 u'disk:bandwidth:write': 1.845029893634008,
                 u'cpu:cache:references': 9204011.733255371,
                 u'cpu:time': 1.4614278780423646,
                 u'ram:used': 8.31435590801817
             }
         ], ['cpu:cache:misses',
             'cpu:cache:references',
             'cpu:time',
             'disk:bandwidth:read',
             'disk:bandwidth:write',
             'disk:operations:read',
             'disk:operations:write',
             'network:bandwidth:receive',
             'network:bandwidth:send',
             'network:packets:receive',
             'network:packets:send',
             'ram:used'], {
             'network:bandwidth:send': 2.7132044007899294,
             'network:packets:send': 868.9455631620594,
             'network:bandwidth:receive': 3.1580354374877495,
             'network:packets:receive': 2472.4175497566625,
             'disk:operations:write': 117.58002353628333,
             'cpu:cache:misses': 8881245.43376613,
             'disk:operations:read': 36.7409199142844,
             'disk:bandwidth:read': 2.157018853047773,
             'disk:bandwidth:write': 6.484938647529316,
             'cpu:cache:references': 24244344.603545003,
             'cpu:time': 5.221978208028486,
             'ram:used': 28.252997909306753
         })
    ])
    def test_prepare_mean_sample(self, samples, metrics, expected):
        mean_sample = prepare_mean_sample(samples, metrics)

        for sample in expected.keys():
            assert mean_sample[sample] == expected[sample]


class TestFilterPeaks(object):
    @pytest.mark.parametrize("samples,expected", [
        ({
             'network:bandwidth:send': [-100.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                        1.0, 1.0, 1.0,
                                        100.0],
             'network:packets:send': [-100.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                      1.0, 1.0, 1.0, 100.0],
             'network:bandwidth:receive': [-100.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                           1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                           1.0, 1.0,
                                           1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                           1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                           1.0,
                                           1.0, 1.0, 1.0, 100.0],
         },
         {
             'network:bandwidth:send': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                        1.0, 1.0, 1.0, 1.0],
             'network:packets:send': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                      1.0, 1.0, 1.0, 1.0],
             'network:bandwidth:receive': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                           1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                           1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                           1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                           1.0, 1.0, 1.0, 1.0],
         })
    ])
    def test_filter_peaks(self, samples, expected):
        test_samples = _filter_peaks(samples)

        for sample in expected.keys():
            assert test_samples[sample] == expected[sample]

#!/usr/bin/env python3

import unittest
from unittest import mock
from temperature_rrd import TemperatureRRD


class TestFakeRRD(unittest.TestCase):
    def setUp(self):
        self.temperature_rrd = TemperatureRRD(rrd_path=None)

    @mock.patch('rrdtool.fetch')
    def test_fetch_for_25s_hard_values(self, mocked_rrdtool_fetch):
        # ((start, stop, step), ds_labels, rows)
        mocked_rrdtool_fetch.return_value = (
            (1521572135, 1521572165, 5),
            ('temp1', 'temp2', 'temp3', 'temp4', 'temp5'),
            [
                (None, None, None, None, None),
                (21.011909836, 22.011909836, 23.011909836, 24.011909836, 25.011909836),
                (21.021902074, 22.021902074, 23.021902074, 24.021902074, 25.021902074),
                (21.031895132, 22.031895132, 23.031895132, 24.031895132, 25.031895132),
                (21.041887248000002, 22.041887248000002, 23.041887248000002, 24.041887248000002, 25.041887248000002),
                (None, None, None, None, None)
            ]
        )

        output = self.temperature_rrd.fetch_for_time(start_time_expression='-25s')

        self.assertEqual(
            {
                'datasets': [{'data': [None,
                                       21.011909836,
                                       21.021902074,
                                       21.031895132,
                                       21.041887248000002],
                              'label': 'temp1'},
                             {'data': [None,
                                       22.011909836,
                                       22.021902074,
                                       22.031895132,
                                       22.041887248000002],
                              'label': 'temp2'},
                             {'data': [None,
                                       23.011909836,
                                       23.021902074,
                                       23.031895132,
                                       23.041887248000002],
                              'label': 'temp3'},
                             {'data': [None,
                                       24.011909836,
                                       24.021902074,
                                       24.031895132,
                                       24.041887248000002],
                              'label': 'temp4'},
                             {'data': [None,
                                       25.011909836,
                                       25.021902074,
                                       25.031895132,
                                       25.041887248000002],
                              'label': 'temp5'}],
                'labels': ['2018-03-20T19:55:35',
                           '2018-03-20T19:55:40',
                           '2018-03-20T19:55:45',
                           '2018-03-20T19:55:50',
                           '2018-03-20T19:55:55']
            },
            output
        )


if __name__ == '__main__':
    unittest.main()

# if __name__ == '__main__':
#     RRD_PATH = 'temperature.rrd'

#     temperature_rrd = TemperatureRRD(RRD_PATH, create_rrd=True)

#     a = .01
#     for _ in range(5):
#         sleep(5)
#         temperature_rrd.update({
#             '28-0416010629ff': 21.0 + a,
#             '28-0416c0b953ff': 22.0 + a,
#             '28-0516b40863ff': 23.0 + a,
#             '28-0516b421e7ff': 24.0 + a,
#             '28-0516b47155ff': 25.0 + a
#         })
#         a += .01

#     pprint(temperature_rrd.fetch_for_time('-25s'), width=1)

#!/usr/bin/env python3

import shutil
import tempfile
import unittest
from random import random
import rrdtool
from unittest import mock

from temperature_monitor.temperature_rrd import TemperatureRRD


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


class TestRealRRD(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.rrd_path = self.tmp_dir + '/tmp_db.rrd'

        rrdtool.create(
            self.rrd_path,
            '--start', '{}s'.format(-20 * 60),
            '--step', '5',
            'DS:temp1:GAUGE:300:U:U',
            'DS:temp2:GAUGE:300:U:U',
            'DS:temp3:GAUGE:300:U:U',
            'DS:temp4:GAUGE:300:U:U',
            'DS:temp5:GAUGE:300:U:U',
            'RRA:AVERAGE:0.5:1:60',
            'RRA:AVERAGE:0.5:4:60',
            'RRA:AVERAGE:0.5:12:60',
            'RRA:AVERAGE:0.5:96:60',
            'RRA:AVERAGE:0.5:288:60',
            'RRA:AVERAGE:0.5:576:60',
            'RRA:AVERAGE:0.5:2016:60',
            'RRA:AVERAGE:0.5:4032:60'
        )

        self.temperature_rrd = TemperatureRRD(
            rrd_path=self.rrd_path
        )

        labels = ':'.join(['temp{}'.format(i + 1) for i in range(5)])

        for x in range(60, 0, -5):
            temperatures = ':'.join([str(21 + random() * 4) for _ in range(5)])
            rrdtool.update(
                self.rrd_path,
                '--template', '{}'.format(labels),
                '--',
                '{}:{}'.format(-x, temperatures)
            )

    def test_basic_output(self):
        output = self.temperature_rrd.fetch_for_time('-30s')

        self.assertIn('datasets', output)
        self.assertIn('labels', output)

    def test_length_of_output(self):
        output = self.temperature_rrd.fetch_for_time('-30s')

        self.assertEqual(len(output['datasets'][0]['data']), 5)
        self.assertEqual(len(output['labels']), 5)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)


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

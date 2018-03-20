#!/usr/bin/env python3

import unittest


class TestSomething(unittest.TestCase):
    def test_ddd(self):
        self.assertTrue(True)


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

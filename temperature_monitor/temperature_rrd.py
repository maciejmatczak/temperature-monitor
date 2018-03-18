#!/usr/bin/env python3

from datetime import datetime
from os import path
import rrdtool
import shutil
from time import sleep
from pprint import pprint

from config import SENSOR_CONFIG


class TemperatureRRD(object):
    def __init__(self, rrd_path, rrd_backup_path=None, create_rrd=False):
        self.rrd_path = rrd_path
        self.rrd_backup_path = rrd_backup_path

        if create_rrd:
            if self.rrd_backup_path and path.exists(self.rrd_backup_path):
                shutil.copy(self.rrd_backup_path, self.rrd_path)
            else:
                rrdtool.create(
                    rrd_path,
                    "--step", "5",
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

    def fetch_for_time(self, start_time_expression, end_time_expression=None):
        ((start, stop, step), ds_labels, rows) = rrdtool.fetch(self.rrd_path, 'AVERAGE',
                                                               '-s', start_time_expression)

        # now len(measurment_matrix) equals number of sensors,
        # every tuple inside is time series of measurments
        measurment_matrix = [list(series) for series in zip(*rows)]

        time_series = [datetime.fromtimestamp(
            x).isoformat() for x in range(start, stop, step)]

        # # getting additional latest value which did not have occasion to be
        # # included in fetched archive
        # if step == 1:
        #     (last_timestamp, last_value) = self.__last_update()
        #     try:
        #         rows[-(stop - last_timestamp)] = last_value
        #     except IndexError:
        #         pass
        for _ in range(2):
            if not any([series[-1] for series in measurment_matrix]):
                for series in measurment_matrix:
                    series.pop(-1)
                time_series.pop(-1)

        output = {
            'labels': time_series,
            'datasets': [{'label': label, 'data': data} for (label, data) in zip(ds_labels, measurment_matrix)]
        }

        return output

    def update(self, temperature_measurments):
        """It uses dictionary with measurments (values) from specific DS thermometers (keys)
        """
        temperature = ':'.join(str(x)
                               for x in temperature_measurments.values())
        labels = ':'.join([SENSOR_CONFIG[sensor]
                           for sensor in temperature_measurments.keys()])

        rrdtool.update(self.rrd_path,
                       '-t', '{}'.format(labels),
                       'N:{}'.format(temperature)
                       )


if __name__ == '__main__':
    RRD_PATH = 'temperature.rrd'

    temperature_rrd = TemperatureRRD(RRD_PATH, create_rrd=True)

    a = .01
    for _ in range(5):
        sleep(5)
        temperature_rrd.update({
            '28-0416010629ff': 21.0 + a,
            '28-0416c0b953ff': 22.0 + a,
            '28-0516b40863ff': 23.0 + a,
            '28-0516b421e7ff': 24.0 + a,
            '28-0516b47155ff': 25.0 + a
        })
        a += .01

    pprint(temperature_rrd.fetch_for_time('-25s'), width=1)

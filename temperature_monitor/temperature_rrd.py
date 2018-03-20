#!/usr/bin/env python3

from datetime import datetime
from os import path
import rrdtool
import shutil

from config import SENSOR_CONFIG


class TemperatureRRD():
    """API for easy access predefined RRD with use of temperature data.

    Returns:
        Object with easy to use descriptive functions.
    """

    def __init__(self, rrd_path: str, rrd_backup_path: str=None, create_rrd: bool=False) -> None:
        """API for temperature type RRD.

        Number of thermometers is predefined in config. Can use backuped db for source or create from scratch.

        Args:
            rrd_path (str): Path to production db.
            rrd_backup_path (str, optional): Defaults to None. Source db to fetch from backup area.
            create_rrd (bool, optional): Defaults to False. Switch to create or not the db on usage.

        Returns:
            None: None.
        """

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

    def fetch_for_time(self, start_time_expression: str) -> dict:
        """Fetches measurments for provided time expression.

        Type expression can be as follows: "-20min"

        Args:
            start_time_expression (str): Start time expression.

        Returns:
            dict: [description]
        """

        ((start, stop, step), ds_labels, rows) = rrdtool.fetch(self.rrd_path, 'AVERAGE',
                                                               '-s', start_time_expression)

        # now len(measurment_matrix) equals number of sensors,
        # every list inside is time series of measurments
        measurment_matrix = [list(series) for series in zip(*rows)]

        time_series = [datetime.fromtimestamp(stamp).isoformat() for stamp in range(start, stop, step)]

        # filtering out few None values from top
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

    def update(self, temperature_measurments: dict):
        """Updates database with new measurment.

        As this are raw data from physical devices, it uses config data to connect thermometer symbols with database
        labels.

        Args:
            temperature_measurments (dict): dictionary with measurments (values) from specific DS thermometers (keys)

            For example:
            temperature_measurments = {
                '28-0516b47155ff': 24.5
                ...
            }
        """
        temperature = ':'.join(str(x)
                               for x in temperature_measurments.values())
        labels = ':'.join([SENSOR_CONFIG[sensor]
                           for sensor in temperature_measurments.keys()])

        rrdtool.update(self.rrd_path,
                       '-t', '{}'.format(labels),
                       'N:{}'.format(temperature)
                       )

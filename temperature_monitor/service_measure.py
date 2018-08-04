from dotenv import load_dotenv
from glob import glob
import logging
from multiprocessing.dummy import Pool
from os import getenv
from os.path import basename
from random import random
from apscheduler.schedulers.blocking import BlockingScheduler as Scheduler

from temperature_rrd import TemperatureRRD

load_dotenv()

temperature_rrd = TemperatureRRD(getenv('RRD_PATH'), getenv('RRD_BACKUP_PATH', default=None), create_rrd=True)
scheduler = Scheduler(timezone="UTC")
pool = Pool(5)
logging.basicConfig()


def read_1wire_temp_device(device_path):
    try:
        with open(device_path + '/w1_slave', "r") as f:
            data = f.readlines()
    except Exception as exception:
        data = None
        logging.exception('Exception during reading sensor data {}'.format(device_path))

    if data and data[0].strip()[-3:] == "YES":
        temperature_raw = float(data[1].split("=")[1]) / 1000
    else:
        temperature_raw = None

    return temperature_raw


def read_1wire_temp_all_parallel():
    global pool

    devices_path_list = sorted(glob('/sys/bus/w1/devices/28*'))
    devices_name_list = [basename(p) for p in devices_path_list]

    result = pool.map(read_1wire_temp_device, devices_path_list)

    return dict(zip(devices_name_list, result))


def scheduled_task():
    temperature_dict = read_1wire_temp_all_parallel()
    temperature_rrd.update(temperature_dict)


def scheduled_task_fake():
    temperature_dict = {
        '28-0416010629ff': 20 + random()*3,
        '28-0416c0b953ff': 20 + random()*3,
        '28-0516b40863ff': 20 + random()*3,
        '28-0516b421e7ff': 20 + random()*3,
        '28-0516b47155ff': 20 + random()*3
    }
    temperature_rrd.update(temperature_dict)


def main():
    if getenv('ENVIRONMENT') == 'DEVELOPMENT':
        task = scheduled_task_fake
    else:
        task = scheduled_task

    scheduler.add_job(task, trigger='cron', second='*/5')


if __name__ == '__main__':
    main()

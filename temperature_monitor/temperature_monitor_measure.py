from glob import glob
import logging
from multiprocessing.dummy import Pool
from os.path import basename
from apscheduler.schedulers.blocking import BlockingScheduler as Scheduler

from temperature_rrd import TemperatureRRD
from config import RRD_PATH, RRD_BACKUP_PATH


temperature_rrd = TemperatureRRD(RRD_PATH, RRD_BACKUP_PATH, create_rrd=True)
scheduler = Scheduler()
pool = Pool(5)

logging.basicConfig()


def read_1wire_temp_device(device_path):
    try:
        with open(device_path + '/w1_slave', "r") as f:
            data = f.readlines()
    except Exception as exception:
        data = None
        logging.exception('Exception durin reading sensor data {}'.format(device_path))

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


@scheduler.scheduled_job("cron", second="*/5")
def scheduled_task():
    temperature_dict = read_1wire_temp_all_parallel()
    temperature_rrd.update(temperature_dict)


def main():
    scheduler.start()


if __name__ == '__main__':
    main()

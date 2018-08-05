import eventlet
eventlet.monkey_patch()
from datetime import datetime  # noqa E402
from dotenv import load_dotenv  # noqa E402
from flask import Flask, render_template, jsonify  # noqa E402
from flask_socketio import SocketIO, emit  # noqa E402
from os import path, system, getenv  # noqa E402
import platform  # noqa E402
from random import random  # noqa E402
import sys  # noqa E402
from temperature_monitor.temperature_rrd import TemperatureRRD  # noqa E402


load_dotenv()

temperature_rrd = TemperatureRRD(getenv('RRD_PATH'))

app = Flask(__name__)
socketio = SocketIO(app, async_mode="eventlet")

start_time = datetime.now()


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@app.route('/chart')
def chart():
    return render_template('chart.html', async_mode=socketio.async_mode)


@app.route('/data/<time>')
def data_request(time):
    global temperature_rrd

    response = temperature_rrd.fetch_for_time(str(time))

    return jsonify(response)


@socketio.on('my_ping')
def ping_pong():
    global start_time

    emit('my_pong')
    emit('uptime', str(datetime.now() - start_time))


def main():
    if getenv('ENVIRONMENT') == 'development':
        socketio.run(app)
    else:
        socketio.run(app, host="0.0.0.0", port=80)


if __name__ == '__main__':
    main()

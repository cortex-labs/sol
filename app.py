from threading import Lock
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from astropy.coordinates import solar_system_ephemeris, get_body_barycentric
from astropy.time import Time, TimeDelta


SCALE = 100000


solar_system_ephemeris.set('jpl')
app = Flask(__name__)
socketio = SocketIO(app)
thread = None
thread_lock = Lock()


def tick():
    count = 0

    while True:
        t = Time.now() + TimeDelta(86400 * count, format='sec')

        mars = get_body_barycentric('Mars', t)
        earth = get_body_barycentric('Earth', t)
        moon = get_body_barycentric('Moon', t)

        socketio.emit('tick', {
            'earth': {
                'x': round(earth.x.value / SCALE, 2),
                'y': round(earth.y.value / SCALE, 2),
                'z': round(earth.z.value / SCALE, 2),
            },
            'moon': {
                'x': round(moon.x.value / SCALE, 2),
                'y': round(moon.y.value / SCALE, 2),
                'z': round(moon.z.value / SCALE, 2),
            },
            'mars': {
                'x': round(mars.x.value / SCALE, 2),
                'y': round(mars.y.value / SCALE, 2),
                'z': round(mars.z.value / SCALE, 2),
            },
            't': str(t),
        })

        socketio.sleep(0.01)

        count += 1


@app.route('/')
def index():
    return render_template('aframe.html')


@socketio.on('connect')
def on_connect():
    global thread

    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=tick)


if __name__ == '__main__':
    socketio.run(app)

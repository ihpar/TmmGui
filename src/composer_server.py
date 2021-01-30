import numpy as np
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from celery import Celery
from parts_composer import compose_zemin, compose_nakarat, compose_meyan, song_2_mus

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lorem_ipman'
socketio = SocketIO(app, async_mode='eventlet')


def make_celery(appl):
    celery = Celery(appl.import_name, backend=appl.config['CELERY_RESULT_BACKEND'],
                    broker=appl.config['CELERY_BROKER_URL'])
    celery.conf.update(appl.config)
    task_base = celery.Task

    class ContextTask(task_base):
        abstract = True

        def __call__(self, *args, **kwargs):
            with appl.app_context():
                return task_base.__call__(self, *args, **kwargs)

    # celery.Task = ContextTask
    return celery


@socketio.on('start_composing', namespace='/compose')
def start_composing(data):
    print(data)
    print('---- thread started! ----')
    print('---- thread started! ----')
    print('---- thread started! ----')


def start_composing_bg(data):
    try:
        makam = data['makam']
        notes = data['notes']

        res = compose_zemin(makam, notes)
        if res['type'] == 'error':
            socketio.emit('composition_status', {'type': 'error', 'section': 'zemin'}, namespace='/compose')
            return

        socketio.emit('composition_status', {'type': 'composed', 'section': 'zemin'}, namespace='/compose')
        print('zemin emit')

        makam = res['makam']
        dir_path = res['dir_path']
        set_size = res['set_size']
        measure_cnt = res['measure_cnt']
        note_dict = res['note_dict']
        oh_manager = res['oh_manager']
        time_sig = res['time_sig']
        part_a = res['part_a']

        res = compose_nakarat(makam, dir_path, set_size, measure_cnt, note_dict, oh_manager, time_sig, part_a)
        if res['type'] == 'error':
            socketio.emit('composition_status', {'type': 'error', 'section': 'nakarat'}, namespace='/compose')
            return

        socketio.emit('composition_status', {'type': 'composed', 'section': 'nakarat'}, namespace='/compose')
        print('nakarat emit')

        part_b = res['part_b']
        second_rep = res['second_rep']

        res = compose_meyan(makam, dir_path, set_size, measure_cnt, note_dict, oh_manager, time_sig, part_b)
        if res['type'] == 'error':
            socketio.emit('composition_status', {'type': 'error', 'section': 'meyan'}, namespace='/compose')
            return

        socketio.emit('composition_status', {'type': 'composed', 'section': 'meyan'}, namespace='/compose')
        print('meyan emit')

        part_c = res['part_c']

        song = np.append(part_a, part_b, axis=1)
        song = np.append(song, part_c, axis=1)

        song_2_mus(song, makam, 'song_name', oh_manager, note_dict, time_sig, '4,8,12', second_rep, to_browser=True)

        socketio.emit('composition_status', {'type': 'composed', 'section': 'all'}, namespace='/compose')
        print('all emit')

    except Exception as e:
        emit('composition_status', {'type': 'error', 'section': 'start_composing', 'msg': str(e)})
        print(e)


@socketio.on('disconnect', namespace='/compose')
def disconnected():
    print('disconnected')


@socketio.on('connect', namespace='/compose')
def connected():
    print('connected')


@socketio.on('message', namespace='/compose')
def handle_message(msg):
    print('message:', msg)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app, debug=True)

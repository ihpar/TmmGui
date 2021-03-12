import numpy as np
import uuid
from flask import Flask, render_template, url_for, jsonify, request, json
from celery import Celery
from parts_composer import compose_zemin, compose_nakarat, compose_meyan, song_2_mus

# T1- redis-server
# T2- celery worker -A composer_server.celery --loglevel=info
# T3- python composer_server.py

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lorem-ipman'

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_TASK_SERIALIZER'] = 'json'
app.config['CELERY_ACCEPT_CONTENT'] = ['json']

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@celery.task(bind=True)
def compose(self, notes):
    post_obj = json.loads(notes)
    makam = post_obj['makam']
    notes = post_obj['notes']
    self.update_state(state='PROGRESS', meta={'status': 'begin'})

    try:
        self.update_state(state='PROGRESS', meta={'status': 'zemin'})
        res = compose_zemin(makam, notes)
        if res['type'] == 'error':
            self.update_state(state='ERROR', meta={'status': 'zemin'})
            return {'status': 'ERROR', 'result': 'zemin'}

        makam = res['makam']
        dir_path = res['dir_path']
        set_size = res['set_size']
        measure_cnt = res['measure_cnt']
        note_dict = res['note_dict']
        oh_manager = res['oh_manager']
        time_sig = res['time_sig']
        part_a = res['part_a']

        self.update_state(state='PROGRESS', meta={'status': 'nakarat'})
        res = compose_nakarat(makam, dir_path, set_size, measure_cnt, note_dict, oh_manager, time_sig, part_a)
        if res['type'] == 'error':
            self.update_state(state='ERROR', meta={'status': 'nakarat'})
            return {'status': 'ERROR', 'result': 'nakarat'}

        part_b = res['part_b']
        second_rep = res['second_rep']

        self.update_state(state='PROGRESS', meta={'status': 'meyan'})
        res = compose_meyan(makam, dir_path, set_size, measure_cnt, note_dict, oh_manager, time_sig, part_b)
        if res['type'] == 'error':
            self.update_state(state='ERROR', meta={'status': 'meyan'})
            return {'status': 'ERROR', 'result': 'meyan'}

        part_c = res['part_c']

        song = np.append(part_a, part_b, axis=1)
        song = np.append(song, part_c, axis=1)

        song_name = makam + '-' + str(uuid.uuid4())
        browser_song = song_2_mus(song, makam, song_name, oh_manager, note_dict, time_sig, '4,8,12', second_rep, to_browser=True)

        return {'status': json.dumps(browser_song), 'result': 'completed'}

    except Exception as e:
        self.update_state(state='ERROR', meta={'status': str(e)})
        return {'status': 'ERROR', 'result': str(e)}


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/start_composer', methods=['POST'])
def start_composer():
    print('== Starting long task ==')
    notes = request.data
    print('== notes ==', notes)
    task = compose.apply_async(args=(notes,))
    return jsonify({}), 202, {'Location': url_for('task_status', task_id=task.id)}


@app.route('/status/<task_id>')
def task_status(task_id):
    task = compose.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
    else:
        # something's wrong...
        response = {
            'state': task.state,
            'status': str(task.info)
        }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)

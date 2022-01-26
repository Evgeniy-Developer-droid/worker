from flask import Flask, request
from models import db, Statistic, Job
from flask_migrate import Migrate
from flask import jsonify
import json
import time
from config import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{}:{}@db:5432/{}".format(DB_USER, DB_PASS, DB_NAME)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)


def get_token():
    headers = request.headers
    if 'Authorization' in headers:
        token = headers['Authorization'].split(' ')[-1]
        return token
    return False


@app.route('/add-job', methods=['POST'])
def add_job():
    if request.method == 'POST':
        token = get_token()
        if not token:
            return jsonify({'message': "Access is denied", "code": 403}), 403
        data = request.get_json()
        new_job = Job(
                job_id=int(data['job']['id']),
                url=data['job']['url'],
                priority=data['job']['priority'],
                callback=data['job']['callback'],
                token=token,
                results=json.dumps({}),
                creation_date=time.time(),
                processing_time=0,
            )
        instance_statistic = Statistic.query.get(1)
        instance_statistic.queue = instance_statistic.queue + 1
        db.session.add(new_job)
        db.session.commit()
        return jsonify({'message': 'Job has been added', "code": 201}), 201
    return jsonify({'message': 'Method GET not allowed', "code": 400}), 400



@app.route('/status')
def status():
    if not get_token():
        return jsonify({'message': "Access is denied", "code": 403}), 403
    instance = Statistic.query.get(1)
    response_data = {"queue": {"processed": 0,"in_progress": 0,"in_queue": 0,"average_processing_time": 0}}
    if not instance:
        new_instance = Statistic()
        db.session.add(new_instance)
        db.session.commit()
    else:
        response_data['queue']['processed'] = instance.processed
        response_data['queue']['in_progress'] = instance.in_progress
        response_data['queue']['in_queue'] = instance.queue
        response_data['queue']['average_processing_time'] = instance.average_processing_time
    return jsonify(response_data), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
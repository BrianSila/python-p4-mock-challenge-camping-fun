#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET'])
def get_campers():

    campers = Camper.query.all()

    if not campers:
        return jsonify({"error": "Camper not found"}), 404

    campers_list = [
        {
            'id': camper.id,
            'name': camper.name,
            "age": camper.age
        } for camper in campers
    ]
    return jsonify(campers_list), 200

@app.route('/campers/<int:id>', methods=['GET'])
def get_camper(id):
    camper = db.session.get(Camper, id)

    if not camper:
        return jsonify({"error": "Camper not found"}), 404

    camper_data = {
        "id": camper.id,
        "name": camper.name,
        "age": camper.age,
        "signups": [
            {
                "id": signup.id,
                "time": signup.time,
                "camper_id": signup.camper_id,
                "activity_id": signup.activity_id,
                "activity": {
                    "id": signup.activity.id,
                    "name": signup.activity.name,
                    "difficulty": signup.activity.difficulty
                }
            }
            for signup in camper.signups
        ]
    }
    return jsonify(camper_data), 200

@app.route('/campers', methods=['POST'])
def create_camper():
    data = request.get_json()

    if not data or not data.get('name') or not data.get('age'):
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        new_camper = Camper(
            name=data.get('name'),
            age=data.get('age')
        )
        db.session.add(new_camper)
        db.session.commit()
    except ValueError:
        return jsonify({"errors": ["validation errors"]}), 400

    return jsonify({
        "id": new_camper.id,
        "name": new_camper.name,
        "age": new_camper.age
    }), 201

@app.route('/campers/<int:id>', methods=['PATCH'])
def update_camper(id):
    record = Camper.query.filter(Camper.id == id).first()

    if not record:
        return jsonify({"error": "Camper not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"errors": ["validation errors"]}), 400
    try:
        for attr, value in data.items():
            setattr(record, attr, value)
        db.session.add(record)
        db.session.commit()
    except ValueError:
        return jsonify({"errors": ["validation errors"]}), 400

    return jsonify({
        'id': record.id,
        'name': record.name,
        'age': record.age
    }), 202

@app.route('/activities', methods=['GET'])
def get_activities():

    activities = Activity.query.all()

    if not activities:
        return jsonify({"error": "Activities not found"}), 404
    
    activity_list = [
        {
            'id': activity.id,
            'name': activity.name,
            'difficulty': activity.difficulty
        } for activity in activities
    ]

    return jsonify(activity_list), 200

@app.route('/activities/<int:id>', methods=['GET'])
def get_activity(id):
    activity = db.session.get(Activity, id)

    if not activity:
        return jsonify({"error": "Activity not found"}), 404
    
    activity_list = [
        {
            'id': activity.id,
            'name': activity.name,
            'difficulty': activity.difficulty
        }
    ]

    return jsonify(activity_list), 200

@app.route('/activities', methods=['POST'])
def create_activity():

    data = request.get_json()

    if not data or not data.get('name') or not data.get('difficulty'):
        return jsonify({"errors": ["validation errors"]}), 400

    new_activity = Activity(
        name=data.get('name'),
        difficulty=data.get('difficulty')
    )

    db.session.add(new_activity)
    db.session.commit()

    return jsonify({
        "id": new_activity.id,
        "name": new_activity.name,
        "difficulty": new_activity.difficulty
    }), 201
    

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = db.session.get(Activity, id)

    if not activity:
        return jsonify({"error": "Activity not found"}), 404
    db.session.delete(activity)
    db.session.commit()

    return '', 204
    

@app.route('/signups', methods=['POST'])
def create_signup():
    data = request.get_json()

    if not data:
        return jsonify({"errors": ["validation errors"]}), 400

    camper_id = data.get('camper_id')
    activity_id = data.get('activity_id')
    time = data.get('time')

    if not camper_id or not activity_id or not isinstance(time, int):
        return jsonify({"errors": ["validation errors"]}), 400

    camper = db.session.get(Camper, camper_id)
    activity = db.session.get(Activity, activity_id)

    if not camper or not activity:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        new_signup = Signup(
            camper_id=camper_id,
            activity_id=activity_id,
            time=time
        )
        db.session.add(new_signup)
        db.session.commit()
    except ValueError:
        return jsonify({"errors": ["validation errors"]}), 400

    return jsonify({
        "id": new_signup.id,
        "camper_id": new_signup.camper_id,
        "activity_id": new_signup.activity_id,
        "time": new_signup.time,
        "activity": {
            "id": activity.id,
            "name": activity.name,
            "difficulty": activity.difficulty
        },
        "camper": {
            "id": camper.id,
            "name": camper.name,
            "age": camper.age
        }
    }), 201

if __name__ == '__main__':
    app.run(port=5555, debug=True)
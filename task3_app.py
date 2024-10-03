from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:irrelevant1@127.0.0.1:3306/fitness_center' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    join_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'join_date': self.join_date.isoformat()
        }

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes

    member = db.relationship('Member', backref=db.backref('workout_sessions', lazy=True))





@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    new_member = Member(name=data['name'], email=data['email'], age=data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify(new_member.to_dict()), 201

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([member.to_dict() for member in members]), 200

@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    member = Member.query.get_or_404(id)
    return jsonify(member.to_dict()), 200

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    data = request.get_json()
    member = Member.query.get_or_404(id)
    member.name = data['name']
    member.email = data['email']
    member.age = data['age']
    db.session.commit()
    return jsonify(member.to_dict()), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return '', 204

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.route('/workout-sessions', methods=['POST'])
def schedule_workout():
    data = request.get_json()
    new_session = WorkoutSession(
        member_id=data['member_id'],
        date=datetime.fromisoformat(data['date']),
        duration=data['duration']
    )
    db.session.add(new_session)
    db.session.commit()
    return jsonify({
        'id': new_session.id,
        'member_id': new_session.member_id,
        'date': new_session.date.isoformat(),
        'duration': new_session.duration
    }), 201

@app.route('/workout-sessions/<int:id>', methods=['PUT'])
def update_workout(id):
    session = WorkoutSession.query.get_or_404(id)
    data = request.get_json()
    session.date = datetime.fromisoformat(data['date'])
    session.duration = data['duration']
    db.session.commit()
    return jsonify({
        'id': session.id,
        'member_id': session.member_id,
        'date': session.date.isoformat(),
        'duration': session.duration
    }), 200

@app.route('/workout-sessions', methods=['GET'])
def get_all_workouts():
    sessions = WorkoutSession.query.all()
    return jsonify([{
        'id': session.id,
        'member_id': session.member_id,
        'date': session.date.isoformat(),
        'duration': session.duration
    } for session in sessions]), 200

@app.route('/members/<int:member_id>/workout-sessions', methods=['GET'])
def get_member_workouts(member_id):
    member = Member.query.get_or_404(member_id)
    sessions = WorkoutSession.query.filter_by(member_id=member_id).all()
    return jsonify([{
        'id': session.id,
        'date': session.date.isoformat(),
        'duration': session.duration
    } for session in sessions]), 200

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
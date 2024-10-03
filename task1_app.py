from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:irrelevant1@127.0.0.1:3306/fitness_center' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    join_date = db.Column(db.DateTime, default=db.func.current_timestamp())

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes

    member = db.relationship('Member', backref=db.backref('workout_sessions', lazy=True))

# Create the database and tables
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)

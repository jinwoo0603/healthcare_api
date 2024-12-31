from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    height = db.Column(db.Float, nullable=True)
    birthdate = db.Column(db.Date, nullable=True)
    gender = db.Column(db.Binary, nullable=True)
    smoking_history = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    doc_no = db.Column(db.Integer, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Carelist(db.Model):
    __tablename__ = 'carelist'
    doc_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    weight = db.Column(db.Float, nullable=True)
    blood_glucose = db.Column(db.Integer, nullable=True)
    blood_pressure = db.Column(db.Integer, nullable=True)
    at = db.Column(db.DateTime, default=datetime.utcnow)

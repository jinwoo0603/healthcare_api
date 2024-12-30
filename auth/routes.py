from flask import Blueprint, request, jsonify
from flask_security import login_user, logout_user
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({"message": "Login successful", "user": {"email": user.email, "id": user.id}})
    return jsonify({"message": "Invalid credentials"}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    height = data.get('height')
    age = data.get('age')
    gender = data.get('gender')
    smoking_history = data.get('smoking_history')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    hashed_password = generate_password_hash(password, method='sha256')
    user = User(
        email=email,
        password=hashed_password,
        height=float(height),
        age=int(age),
        gender=gender,
        smoking_history=bool(smoking_history)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully", "user": {"email": user.email, "id": user.id}})

@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"})

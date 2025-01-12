from flask import Blueprint, request, jsonify
from flask_security import login_user, logout_user
from models import db, User, Doctor
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login/user', methods=['POST'])
def login_user_route():
    """
    사용자(User) 로그인
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # 이메일로 사용자 검색
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid email or password"}), 401

    login_user(user, remember=True)
    return jsonify({
        "message": "User login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }), 200


@auth_bp.route('/login/doctor', methods=['POST'])
def login_doctor_route():
    """
    의사(Doctor) 로그인
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # 이메일로 의사 검색
    doctor = Doctor.query.filter_by(email=email).first()

    if not doctor or not check_password_hash(doctor.password, password):
        return jsonify({"message": "Invalid email or password"}), 401

    login_user(doctor)
    return jsonify({
        "message": "Doctor login successful",
        "doctor": {
            "id": doctor.id,
            "email": doctor.email,
            "name": doctor.name,
            "doc_no": doctor.doc_no
        }
    }), 200

@auth_bp.route('/register/user', methods=['POST'])
def register_user():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    height = data.get('height')
    birthdate = data.get('birthdate')  # YYYY-MM-DD 형식
    gender = data.get('gender')
    smoking_history = data.get('smoking_history')
    social_id = data.get('social_id')  # 주민등록번호

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400
    if User.query.filter_by(social_id=generate_password_hash(social_id)).first():
        return jsonify({"message": "Social ID already exists"}), 400

    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(
        email=email,
        password=hashed_password,
        name=name,
        height=float(height) if height else None,
        birthdate=datetime.strptime(birthdate, '%Y-%m-%d') if birthdate else None,
        gender=gender.encode() if gender else None,
        smoking_history=int(smoking_history) if smoking_history else None
    )
    new_user.set_social_id(social_id)  # 주민등록번호 해싱 후 저장

    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/register/doctor', methods=['POST'])
def register_doctor():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    doc_no = data.get('doc_no')

    if Doctor.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400
    if Doctor.query.filter_by(doc_no=doc_no).first():
        return jsonify({"message": "Doctor number already exists"}), 400

    hashed_password = generate_password_hash(password, method='sha256')
    new_doctor = Doctor(
        email=email,
        password=hashed_password,
        name=name,
        doc_no=int(doc_no)
    )
    db.session.add(new_doctor)
    db.session.commit()
    return jsonify({"message": "Doctor registered successfully"}), 201

@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"})

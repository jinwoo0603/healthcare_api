from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from werkzeug.security import check_password_hash
from models import db, User, Doctor, Carelist

care_bp = Blueprint('care', __name__)

@care_bp.route('/care', methods=['POST'])
@login_required
def care_route():
    """
    주민등록번호(social_id)를 기반으로 carelist에 의사와 환자 관계를 추가
    """
    data = request.json
    social_id = data.get('social_id')  # 요청 바디에서 주민등록번호 받음

    # 요청을 보낸 유저가 doctors 테이블에 있는지 확인
    doctor = Doctor.query.filter_by(email=current_user.email).first()
    if not doctor:
        return jsonify({"message": "Unauthorized. Only doctors can perform this action."}), 403

    # 주민등록번호를 가진 유저 조회
    user = User.query.filter_by().all()
    found_user = None
    for u in user:
        if u.verify_social_id(social_id):
            found_user = u
            break
    if not found_user:
        return jsonify({"message": "No user found with the provided Social ID"}), 404

    # carelist에 의사와 유저의 관계 추가
    existing_relationship = Carelist.query.filter_by(doc_id=doctor.id, user_id=found_user.id).first()
    if existing_relationship:
        return jsonify({"message": "This care relationship already exists"}), 400

    new_care = Carelist(doc_id=doctor.id, user_id=found_user.id)
    db.session.add(new_care)
    db.session.commit()

    return jsonify({
        "message": "Care relationship added successfully",
        "care": {
            "doctor_id": doctor.id,
            "user_id": found_user.id
        }
    }), 201

@care_bp.route('/care', methods=['DELETE'])
@login_required
def delete_care_relationship():
    """
    주민등록번호(social_id)를 기반으로 carelist에서 의사와 환자 관계를 삭제
    """
    data = request.json
    social_id = data.get('social_id')  # 요청 바디에서 주민등록번호 받음

    # 요청을 보낸 유저가 doctors 테이블에 있는지 확인
    doctor = Doctor.query.filter_by(email=current_user.email).first()
    if not doctor:
        return jsonify({"message": "Unauthorized. Only doctors can perform this action."}), 403

    # 주민등록번호를 가진 유저 조회
    user = User.query.filter_by().all()
    found_user = None
    for u in user:
        if u.verify_social_id(social_id):
            found_user = u
            break
    if not found_user:
        return jsonify({"message": "No user found with the provided Social ID"}), 404

    # carelist에서 관계 삭제
    relationship = Carelist.query.filter_by(doc_id=doctor.id, user_id=found_user.id).first()
    if not relationship:
        return jsonify({"message": "No such care relationship exists"}), 404

    db.session.delete(relationship)
    db.session.commit()

    return jsonify({
        "message": "Care relationship deleted successfully",
        "care": {
            "doctor_id": doctor.id,
            "user_id": found_user.id
        }
    }), 200

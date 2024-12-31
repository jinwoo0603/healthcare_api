from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from models import db, History

history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['POST'])
@login_required
def create_history():
    """
    로그인한 유저가 blood_glucose, weight, blood_pressure 데이터를 보내면
    History 테이블에 저장합니다.
    """
    data = request.json
    blood_glucose = data.get('blood_glucose')
    weight = data.get('weight')
    blood_pressure = data.get('blood_pressure')

    # 입력 값 검증
    if blood_glucose is None or weight is None or blood_pressure is None:
        return jsonify({"message": "All fields are required"}), 400

    # History 데이터 생성
    new_history = History(
        user_id=current_user.id,
        blood_glucose=int(blood_glucose),
        weight=float(weight),
        blood_pressure=int(blood_pressure)
    )
    
    db.session.add(new_history)
    db.session.commit()
        
    # AI 모델 적용 코드 추가할것

    return jsonify({
        "message": "History record created successfully",
        "history": {
            "user_id": new_history.user_id,
            "blood_glucose": new_history.blood_glucose,
            "weight": new_history.weight,
            "blood_pressure": new_history.blood_pressure,
            "at": new_history.at
        }
    }), 201

from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from sqlalchemy.sql import func
from models import db, History
import pandas as pd
import joblib
import datetime as dt

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
    
    height = current_user.height
    smoking_history = current_user.smoking_history
    age = dt.datetime.now().year - current_user.birthdate.year
    bmi = weight / (height / 100.0) ** 2
    gender = int(current_user.gender)

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
        
    # AI 모델 적용
    scaler = joblib.load("../ml/diabetes_scaler.pkl")
    pca = joblib.load("../ml/diabetes_pca.pkl")
    hbA1c = joblib.load("../ml/hbA1c.pkl")
    heart = joblib.load("../ml/heart.pkl")
    
    pred_data = pd.DataFrame([{
        'gender': gender,
        'age': age,
        'hypertension': 1 if blood_pressure > 140 else 0,
        'heart_disease': 0,
        'smoking_history': smoking_history,
        'bmi': bmi,
        'HbA1c_level': 0,
        'blood_glucose_level': blood_glucose,
        'diabetes': 0
    }])
    
    data_scaled = scaler.transform(pred_data)
    data_scaled = pd.DataFrame(data_scaled, columns=data.columns)
    data_pca = pca.transform(data_scaled)
    data_scaled['pca1'] = data_pca[:,0]
    data_scaled['pca2'] = data_pca[:,1]
    data_scaled['pca3'] = data_pca[:,2]
    
    X_hb1ac = data_scaled[['blood_glucose_level', 'pca1', 'pca2', 'pca3']]
    X_heart = data_scaled[['gender', 'hypertension', 'pca1', 'pca3']]
    
    hbA1c_pred = hbA1c.predict(X_hb1ac)[0]
    heart_pred = heart.predict(X_heart)[0]
    
    return jsonify({
        "message": "History record created successfully",
        "history": {
            "user_id": new_history.user_id,
            "blood_glucose": new_history.blood_glucose,
            "weight": new_history.weight,
            "blood_pressure": new_history.blood_pressure,
            "at": new_history.at
        },
        "prediction": {
            "hbA1c": float(hbA1c_pred),
            "heart": float(heart_pred)
        }
    }), 201

@history_bp.route('/history', methods=['GET'])
@login_required
def view_history():
    """
    로그인한 유저의 최근 기록 및 전체 기록 평균을 반환합니다.
    """
    user_id = current_user.id

    # 최근 기록
    recent_record = History.query.filter_by(user_id=user_id).order_by(History.at.desc()).first()

    # 전체 기록 평균 계산
    averages = db.session.query(
        func.avg(History.blood_glucose).label('avg_blood_glucose'),
        func.avg(History.weight).label('avg_weight'),
        func.avg(History.blood_pressure).label('avg_blood_pressure')
    ).filter_by(user_id=user_id).one()

    if not recent_record:
        return jsonify({
            "message": "No history records found for the user.",
            "recent_record": None,
            "averages": {
                "avg_blood_glucose": None,
                "avg_weight": None,
                "avg_blood_pressure": None
            }
        }), 200

    # 결과 반환
    return jsonify({
        "message": "History summary retrieved successfully.",
        "recent_record": {
            "blood_glucose": recent_record.blood_glucose,
            "blood_pressure": recent_record.blood_pressure,
            "weight": recent_record.weight,
            "timestamp": recent_record.at.strftime('%Y-%m-%d %H:%M:%S')
        },
        "averages": {
            "avg_blood_glucose": round(averages.avg_blood_glucose, 2) if averages.avg_blood_glucose else None,
            "avg_weight": round(averages.avg_weight, 2) if averages.avg_weight else None,
            "avg_blood_pressure": round(averages.avg_blood_pressure, 2) if averages.avg_blood_pressure else None
        }
    }), 200
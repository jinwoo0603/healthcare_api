from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_cors import CORS
from models import db, User, Doctor, Carelist, History
from auth.routes import auth_bp
from history.routes import history_bp
from care.routes import care_bp

app = Flask(__name__)
CORS(app, supports_credentials=True)  # 세션 쿠키 전송 허용
app.config.from_pyfile('config.py')

# 데이터베이스 및 Flask-Security 초기화
db.init_app(app)
user_datastore = SQLAlchemyUserDatastore(db, User, Doctor, Carelist, History)
security = Security(app, user_datastore)

# Blueprint 등록
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(history_bp, url_prefix='/api/history')
app.register_blueprint(care_bp, url_prefix='/api/care')

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

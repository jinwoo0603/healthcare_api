from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from models import db, Role, User
from auth.routes import auth_bp

app = Flask(__name__)
app.config.from_pyfile('config.py')

# 데이터베이스 및 Flask-Security 초기화
db.init_app(app)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Blueprint 등록
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

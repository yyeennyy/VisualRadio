import sys
from flask import redirect, url_for, request, Flask
from flask_cors import CORS
import logging

from flask_sqlalchemy import SQLAlchemy


# db

# 로거
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler('my.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

db = SQLAlchemy()
app = Flask(__name__)


def create_app():
    global db
    global app
    CORS(app)  # 모든 라우트에 대해 CORS 허용
    app.config['MAX_CONTENT_LENGTH'] = 800 * 1024 * 1024  # 16MB로 업로드 크기 제한 변경
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://visualradio:visualradio@mysql:3306/radio'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # DB세팅
    # 주의! create database radio; 까지는 되어있어야 함
    db.init_app(app)

    # 블루프린트 인스턴스 가져오기 & flask app에 등록하기
    from VisualRadio.route import auth
    app.register_blueprint(auth, url_prefix='/')

    with app.app_context():
        db.create_all()
    logger.debug("[DB] 생성 완료")

    return app, db







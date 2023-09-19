import sys
from flask import Flask
from flask_cors import CORS
import logging
import logging.handlers
from flask_sqlalchemy import SQLAlchemy
# from flask_socketio import SocketIO

#TODO: 마이그레이션
# for using alembic! with SQLAlchemy.. 
# 마이그레이션 명령어 사용 예
# alembic revision --autogenerate -m "radio에 컬럼 추가.."
# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()
# target_matadata = Base.metadata


# 로거
def CreateLogger(logger_name):
    # Create Logger
    logger = logging.getLogger(logger_name)
    # Check handler exists
    if len(logger.handlers) > 0:
        return logger # Logger already exists
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s |%(levelname)s|%(filename)12s:%(lineno)-4s...%(name)10s > %(message)s', '%Y-%m-%d %H:%M:%S')

    # Create Handlers
    # 1
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    # 2
    file_handler = logging.FileHandler('my.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db = SQLAlchemy()
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 800 * 1024 * 1024  # 16MB로 업로드 크기 제한 변경
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://visualradio:visualradio@mysql:3306/radio'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
# Session = sessionmaker(engine)
logger = CreateLogger("(^o^)b")


def create_app():
    global db
    global app
    # global engine

    CORS(app)  # 모든 라우트에 대해 CORS 허용

    # DB세팅
    db.init_app(app)

    # 블루프린트 인스턴스 가져오기 & flask app에 등록하기
    from route import auth
    app.register_blueprint(auth, url_prefix='/')

    with app.app_context():
        db.create_all() 

    logger.debug("초기화")
    return app, db





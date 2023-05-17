from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db_uri = 'mysql+pymysql://root:visualradio@localhost:3305/radio'
engine = create_engine(db_uri, echo=True)

# 세션 선언과 생성
db_session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine
))
# SQLAlchemy Base Instance 생성
Base = declarative_base()
Base.query = db_session.query_property()

def init_database():
    Base.metadata.create_all(bind=engine)
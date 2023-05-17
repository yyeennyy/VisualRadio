import unittest
from init_db import db_session, engine, Base
from model import Wav
from sqlalchemy.sql import text
import json

# 메모리 db를 만드는 방법 아님! 기존 mysql 연결하는 방식
class DB_Test(unittest.TestCase):
    
    def setUp(self):
        # Wav 테이블 생성
        Base.metadata.create_all(bind=engine)

        # 데이터 삽입
        name, date, broadcast = 'brunchcafe', '2023-05-17', 'MBC'
        db_session.add(Wav(radio_name=name, radio_date=date, broadcast=broadcast, raw=True, section=0, stt=False,
            script=False, contents=False))
        name, date, broadcast = 'brunchcafe', '2023-05-15', 'MBC'
        db_session.add(Wav(radio_name=name, radio_date=date, broadcast=broadcast, raw=True, section=0, stt=False,
            script=False, contents=False))
        name, date, broadcast = 'brunchcafe', '2023-04-04', 'MBC'
        db_session.add(Wav(radio_name=name, radio_date=date, broadcast=broadcast, raw=True, section=0, stt=False,
            script=False, contents=False))
        name, date, broadcast = 'radio11', '2023-04-06', 'KBS'
        db_session.add(Wav(radio_name=name, radio_date=date, broadcast=broadcast, raw=True, section=0, stt=False,
            script=False, contents=False))
        name, date, broadcast = 'happy', '2023-04-08', 'KBS'
        db_session.add(Wav(radio_name=name, radio_date=date, broadcast=broadcast, raw=True, section=0, stt=False,
            script=False, contents=False))
        db_session.commit()

    def tearDown(self):    # Delete all rows from the Wav table
        db_session.query(Wav).delete()
        db_session.commit()
        Wav.__table__.drop(bind=engine) # 중요한 사실! commit과 drop의 순서를 바꾸면 block상태가 되는듯
        db_session.remove()


    def test_get_radio_names_by_broadcast(self):

            # broadcast별로 radio_name을 가져오는 쿼리
            # query = text('SELECT broadcast, radio_name FROM Wav GROUP BY broadcast, radio_name')
            query = text("""
            SELECT CONCAT("{'broadcast':'", broadcast, "',", "'programs':[", GROUP_CONCAT(DISTINCT CONCAT("{'radio_name':'", radio_name, "'}") SEPARATOR ','),']}')
            FROM Wav
            GROUP BY broadcast;
            """)
            result = db_session.execute(query)

            json_data = []
            for r in result:
                print(type(r[0]), r[0])
                json_data.append(json.dumps(r[0]))

            # for data in json_data:
                # print(type(data), data)
            print(json_data)

            # result = db.execute(query)
            # print(result)
            
            # # 결과 검증
            # for row in result:
            #     print(row[0], row[1])
            #     # broadcast = row[0]
            #     # radio_names = row[1]


if __name__ == '__main__':
    unittest.main()



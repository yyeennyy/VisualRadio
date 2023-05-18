import unittest
from init_db import db_session, engine, Base
from model import Wav
from sqlalchemy.sql import text
import json
import os
# from flask import jsonify

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
            query = text("""
            SELECT CONCAT(CONCAT('{"broadcast": "', broadcast, '", ', '"programs": [', GROUP_CONCAT(DISTINCT CONCAT('{"radio_name":"', radio_name, '"}') SEPARATOR ', '),']}'))
            FROM Wav
            GROUP BY broadcast;
            """)
            result = db_session.execute(query)
            dict_list = []
            for r in result:
                # print(json.loads(r[0]))
                dict_list.append(json.loads((r[0])))

            for i in range(len(dict_list)):
                broadcast = dict_list[i]['broadcast']
                for j in dict_list[i]['programs']:
                    radio_name = j['radio_name']
                    img_path = f"/static/{broadcast}/{radio_name}/main_img.png"
                    if os.path.exists(img_path):
                        j['img'] = img_path
                    else:
                        j['img'] = "/static/images/default_main.png"
            print(dict_list)

if __name__ == '__main__':
    unittest.main()



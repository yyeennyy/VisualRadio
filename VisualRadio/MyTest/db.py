import unittest
import datetime
from flask import Flask, jsonify
import sys
sys.path.append('VisualRadio')
from models import Wav
from app import app

class TestMyApp(unittest.TestCase):

    def test_1(radio_name, month):
        with app.app_context():
            # month를 이용하여 시작일과 종료일 계산
            start_date = datetime.strptime(f'{month}-01', '%Y-%m-%d').date()
            end_date = datetime.strptime(f'{month}-01', '%Y-%m-%d').replace(day=1, month=start_date.month+1) - timedelta(days=1)
            
            # 해당 월의 데이터 조회
            dates = Wav.query.filter_by(radio_name=radio_name).filter(Wav.radio_date >= start_date, Wav.radio_date <= end_date).all()
            
            # dates에서 날짜형식 중 특정 month인 데이터의 '일자'를 가져와야 한다.
            dates_json = jsonify([date.as_dict() for date in dates])
            return dates_json

if __name__ == '__main__':
    unittest.main()
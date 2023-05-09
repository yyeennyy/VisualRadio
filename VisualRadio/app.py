import sys
sys.path.append("d:\jp\env\lib\site-packages")

from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import logging
import json
import os
import services
from models import db;
import threading


app = Flask(__name__)
CORS(app)  # 모든 라우트에 대해 CORS 허용

# 로거
# app.logger.setLevel(logging.DEBUG)

# DB세팅
# 주의! create database radioDB; 까지는 되어있어야 함
app.config.from_pyfile('config.py')
db.init_app(app)
with app.app_context():
    db.create_all()  # 테이블이 자동으로 생성되는 명령


# --------------------------------------------------------------------------------- 페이지
@app.route('/admin')
def adminpage():
    return send_from_directory('../VisualRadio/static/html/', 'admin.html')


@app.route('/mainpage')
def mainpage():
    return send_from_directory('../VisualRadio/static/html/', 'main.html')


# --------------------------------------------------------------------------------- admin페이지의 업로드 프로세스
@app.route('/admin-update', methods=['POST'])
def admin_update():
    broadcasting_company = request.form.get('broadcasting_company')
    program_name = request.form.get('program_name')
    date = request.form.get('date')
    guest_info = request.form.get('guest_info')
    audio_file = request.files.get('audio_file')
    audio_save(broadcasting_company, program_name, date, audio_file)
    print("[업로드] 등록 완료:", broadcasting_company, program_name, date, guest_info, audio_file)

    # 다른 프로세스를 백그라운드로 실행시키기
    print("[업로드] 음성처리 - 백그라운드로 시작")
    path = f"./VisualRadio/radio_storage/{broadcasting_company}/{program_name}/{date}/"
    t = threading.Thread(target=process_audio_file, args=(broadcasting_company, program_name, date))
    t.start()
    return "ok"


def process_audio_file(broadcast, name, date):
    services.split(broadcast, name, date)
    services.wavToFlac(broadcast, name, date)
    services.stt(broadcast, name, date)
    services.make_txt(broadcast, name, date)
    print("[업로드] 오디오 처리 완료")
    return "ok"


def audio_save(broadcast, program_name, date, audiofile):
    # 문제점: brunchcafe와 이석훈의브런치카페는 동일한 프로그램임. 추후 이 점 고려해야 할 것임
    path = f"./VisualRadio/radio_storage/{broadcast}/{program_name}/{date}/"
    os.makedirs(path, exist_ok=True)
    audiofile.save(os.path.join(path, 'raw.wav'))
    print("[업로드] raw.wav 저장 완료")
    # DB에 업데이트
    services.audio_save_db(broadcast, program_name, date)
    print("[업로드] DB반영 완료")
    return "ok"


# --------------------------------------------------------------------------------- 미사용
@app.route('/start', methods=['POST'])
def start(wav):
    # 넘어온 json 데이터 처리
    json_data = request.json  # key = radio_name, radio_date
    radio_name = json_data[0]
    date = json_data[1]

    # TODO: 이미 처리한 회차인지 체크하기
    # - DB에서 완료여부 확인
    # - ▼ 미처리 회차라면 쭉 진행

    # 서비스 로직 수행
    try:
        # 분할
        services.split(radio_name, date)

        # stt
        services.stt(radio_name, date)

        # txt 컨텐츠 제작
        services.make_txt(radio_name, date)

        return jsonify({'message': '컨텐츠화 완료'}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# --------------------------------------------------------------------------------- 프론트 요청
# 전체 라디오 프로그램 정보 요청
@app.route('/all')
def get_all():
    all = services.get_all_radio_programs()
    return jsonify(all)


# 라디오 프로그램 이름, 날짜 요청 ㅇ (위 메서드 대신 있는 임시 요청)
@app.route('/program_info', methods=['GET'])
def get_program_info():
    # 임시로 박아두자 (sub2 페이지 하나니까)
    program_info = {
        'radio_name': 'brunchcafe',
        'date': '230226'
    }
    return jsonify(program_info)


# 지정된 회차의 스크립트 요청
@app.route('/<string:radio_name>/<string:date>/script', methods=['GET'])
def get_script(radio_name, date):
    json_data = read_json_file(storage_path(radio_name, date) + '\\result\\script.json')
    return jsonify(json_data)


# 지정된 회차의 섹션 정보 리턴
@app.route('/<string:radio_name>/<string:date>/section', methods=['GET'])
def get_sections(radio_name, date):
    json_data = read_json_file(storage_path(radio_name, date) + '\\result\\section_time.json')
    return json_data


# 지정된 회차의 이미지들 리턴
@app.route('/<string:radio_name>/<string:date>/images', methods=['GET'])
def get_images(radio_name, date):
    file_path = storage_path(radio_name, date) + '\\result\\section_image.json'
    data = read_json_file(file_path)
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    # # JSON 응답 생성
    # response = make_response(data)
    # response.headers['Content-Type'] = 'application/json'
    # response.headers['Access-Control-Allow-Origin'] = '*'
    return response


# 지정된 회차의 음성 데이터 리턴
# 이렇게 코드를 변경하면, send_file 함수가 파일을 열고 전송한 후 파일 객체를 닫기 때문에 net::ERR_CONNECTION_RESET 200 (OK) <- 이 문제 해결 가능
@app.route('/<string:radio_name>/<string:date>/wave', methods=['GET'])
def get_wave(radio_name, date):
    filepath = storage_path(radio_name, date) + '\\raw.wav'
    return send_file(filepath, mimetype="audio/wav", as_attachment=False)
    # return jsonify({'wave':"/VisualRadio/radio_storage/%s/%s/raw.wav"%(radio_name, date)})


# 고정음성 요청
@app.route('/<string:radio_name>/<string:date>/fixed/<string:name>', methods=['GET'])
def get_fixed_wave(radio_name, date, name):
    wav = open(storage_path(radio_name, date) + '\\fixed_wav\\' + name, 'rb')
    response = send_file(wav, mimetype="audio/wav", as_attachment=False)
    return response


# TODO: 지정된 회차의 전체 text
@app.route('/<string:radio_name>/<string:date>/txt', methods=['GET'])
def get_txt(radio_name, date):
    # time, text 키를 가진 json데이터를, text만 있는 문자열로 바꾼다.
    script_path = storage_path(radio_name, date) + '\\result\\script.json'
    txt = ''
    return jsonify(txt)


# 광고 컨텐츠 (미사용)
@app.route('/ad', methods=['GET'])
def get_ad():
    # (프로토타입) 고정된 광고 컨텐츠 리턴
    return open('./VisualRadio/templates/ad.html', encoding='utf-8')


@app.route('/test')
def test():
    services.split('MBC', 'brunchcafe', '2023-02-26')
    services.wavToFlac('MBC', 'brunchcafe', '2023-02-26')
    services.stt('MBC', 'brunchcafe', '2023-02-26')
    services.make_txt('MBC', 'brunchcafe', '2023-02-26')
    return 'test완료! html로 가서 결과를 테스트하세요'


###################################################################################

def storage_path(radio_name, radio_date):
    return os.getcwd() + '\\VisualRadio\\radio_storage\\' + radio_name + '\\' + radio_date


def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


########################
from flask import Flask, send_from_directory


# brunchcafe라디오의 230226날짜로 고정된 화면이 보여진다.
@app.route('/brunchcafe/230226')
def send_static():
    return send_from_directory('../VisualRadio/static/html/', 'sub2.html')


########################

if __name__ == '__main__':
    app.run(debug=False)




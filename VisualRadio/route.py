from flask import Blueprint
from flask import Flask, request, jsonify, send_file, make_response, render_template, redirect, url_for, request
import sys
sys.path.append('./VisualRadio')
import services
import json
import os
import threading

auth = Blueprint('auth', __name__)


# 로거
from VisualRadio import CreateLogger
logger = CreateLogger("우리가1등(^o^)b")



# --------------------------------------------------------------------------------- 수집기
@auth.route('/collector', methods=["POST"])
def collector():
    params = json.loads(request.get_data())
    broadcast = params['broadcast']
    time = params['start_time']
    logger.debug(broadcast, time)
    return services.collector_needs(broadcast, time)

# --------------------------------------------------------------------------------- 페이지
@auth.route('/admin')
def adminpage():
    return render_template('admin.html')

@auth.route('/')
def mainpage():
    return render_template('main.html')


# 임시 
@auth.route('/programs')
def progs():
    return render_template('programs.html')
@auth.route('/all')
def get_all():
    all = services.get_all_radio_programs()
    return jsonify(all)



# --------------------------------------------------------------------------------- admin페이지의 업로드 프로세스
@auth.route('/admin-update', methods=['POST'])
def admin_update():
    logger.debug(f"[업로드] 호출됨")
    broadcast = request.form.get('broadcast')
    program_name = request.form.get('program_name')
    date = request.form.get('date')
    guest_info = request.form.get('guest_info')
    audio_file = request.files.get('audio_file')
    logger.debug(f"[업로드] 값을 가져옴 - {broadcast} {program_name} {date}")
    audio_save(broadcast, program_name, date, audio_file)
    logger.debug(f"[업로드] 등록 완료: {broadcast}, {program_name}, {date}, {guest_info}")

    # 다른 프로세스를 백그라운드로 실행시키기
    logger.debug("[업로드] 음성처리 - 백그라운드로 시작")
    t = threading.Thread(target=process_audio_file, args=(broadcast, program_name, date))
    t.start()
    return "ok"


def process_audio_file(broadcast, name, date):
    logger.debug(f"{broadcast} {name} {date}")
    # services.split(broadcast, name, date)
    # services.stt(broadcast, name, date)
    # services.make_script(broadcast, name, date)
    services.register_listener(broadcast, name, date)
    services.sum_wav_sections(broadcast, name, date)
    logger.debug("[업로드] 오디오 처리 완료")
    return "ok"

def audio_save(broadcast, program_name, date, audiofile):
    path = f"./VisualRadio/radio_storage/{broadcast}/{program_name}/{date}/"
    # 문제점: brunchcafe와 이석훈의브런치카페는 동일한 프로그램임. 추후 이 점 고려해야 할 것임
    # DB에서 체크하는 방식으로 변경해야 함
    if os.path.exists(path + '/raw.wav'):
        logger.debug("[업로드] 이미 raw.wav가 존재함")
    else:
        logger.debug(f"[업로드] raw.wav 저장 시작 - {broadcast} {program_name} {date}")
        os.makedirs(path, exist_ok=True)
        audiofile.save(path + 'raw.wav')
        logger.debug("[업로드] raw.wav 저장 완료")
        # DB에 업데이트
    services.audio_save_db(broadcast, program_name, date)
    logger.debug("[업로드] DB 초기화 완료")
    return "ok"

# -------------------------------------------------------------------------------- 검색기능
@auth.route("/search")
def search_page():
    return render_template('search.html')

@auth.route("/search/program")
def search_program():
    search = request.args.get('search')
    data = services.search_programs(search)
    logger.debug(f"[search] 검색 결과 {data}")
    return json.dumps(data)

@auth.route("/search/listener")
def search_listener():
    search = request.args.get('search')
    data = services.search_listeners(search)
    logger.debug(f"[search] 검색 결과 {data}")
    return json.dumps(data)

# --------------------------------------------------------------------------------- 좋아요 전용
@auth.route("/like/<string:broadcast>/<string:radio_name>", methods=['GET'])
def like(broadcast, radio_name):
    like_cnt = services.like(broadcast, radio_name)
    return json.dumps({'like_cnt':like_cnt})

@auth.route("/unlike/<string:broadcast>/<string:radio_name>", methods=['GET'])
def unlike(broadcast, radio_name):
    like_cnt = services.unlike(broadcast, radio_name)
    return json.dumps({'like_cnt':like_cnt})

# sub1페이지 전용
@auth.route("/like-cnt/<string:broadcast>/<string:radio_name>", methods=['GET'])
def like_prog(broadcast, radio_name):
    like_cnt = services.get_like_cnt(broadcast, radio_name)
    return json.dumps({'like_cnt':like_cnt})



# --------------------------------------------------------------------------------- main

@auth.route('/radio', methods=['GET'])
def radio_all():
    return services.get_all_radio()
    
@auth.route('/subpage', methods=['GET', 'POST'])
def to_sub1():
    return render_template('sub1.html')

# --------------------------------------------------------------------------------- sub1

@auth.route('/<string:broadcast>/<string:radio_name>/img', methods=['GET'])
def load_main_img(broadcast, radio_name):
    img_path = f"/static/{broadcast}/{radio_name}/main_img.png"
    if not os.path.exists(img_path):
        img_path = "/static/images/default_main.png"
    return json.dumps({'main_photo':img_path})

@auth.route('/<string:broadcast>/<string:radio_name>/<string:month>/all', methods=['GET'])
def load_month_info(broadcast, radio_name, month):
    return json.dumps(services.all_date_of(broadcast, radio_name, month))

@auth.route('/<string:radio_name>/radio_info', methods=['GET'])
def load_radio_info(radio_name):
    return json.dumps({'info':"일단 띄워지는것좀 보자"})

@auth.route('/contents', methods=['GET'])
def to_sub2():
    return render_template('sub2.html')



# --------------------------------------------------------------------------------- sub2

# 지정된 회차의 스크립트 요청
@auth.route('/<string:broadcast>/<string:name>/<string:date>/script', methods=['GET'])
def get_script(broadcast, name, date):
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    json_data = read_json_file(path + '/result/script.json')
    return jsonify(json_data)


# 지정된 회차의 섹션 정보 리턴
# @auth.route('/<string:broadcast>/<string:name>/<string:date>/section', methods=['GET'])
# def get_sections(broadcast, name, date):
#     path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
#     json_data = read_json_file(path + '/result/section_time.json')
#     return json_data


# 지정된 회차의 이미지들 리턴
@auth.route('/<string:broadcast>/<string:name>/<string:date>/images', methods=['GET'])
def get_images(broadcast, name, date):
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    file_path = path + '/result/section_image.json'
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
@auth.route('/<string:broadcast>/<string:name>/<string:date>/wave', methods=['GET'])
def get_wave(broadcast, name, date):
    # TODO: 섹션을 합쳐서 리턴한다.

    return send_file(f"radio_storage/{broadcast}/{name}/{date}/sum.wav", mimetype="audio/wav", as_attachment=False)


# # 고정음성 요청
# @auth.route('/<string:radio_name>/<string:date>/fixed/<string:name>', methods=['GET'])
# def get_fixed_wave(broadcast, name, date):
#     path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
#     wav = open(path + '/fixed_wav/' + name, 'rb')
#     response = send_file(wav, mimetype="audio/wav", as_attachment=False)
#     return response


# # TODO: 지정된 회차의 전체 text
# @auth.route('/<string:radio_name>/<string:date>/txt', methods=['GET'])
# def get_txt(radio_name, date):
#     # time, text 키를 가진 json데이터를, text만 있는 문자열로 바꾼다.
#     script_path = storage_path(radio_name, date) + '\\result\\script.json'
#     txt = ''
#     return jsonify(txt)


# 광고 컨텐츠 (미사용)
@auth.route('/ad', methods=['GET'])
def get_ad():
    # (프로토타입) 고정된 광고 컨텐츠 리턴
    return open('./VisualRadio/templates/ad.html', encoding='utf-8')


@auth.route('/test')
def test():
    # services.split('MBC', 'brunchcafe', '2023-02-26')
    # services.wavToFlac('MBC', 'brunchcafe', '2023-02-26')
    # services.stt('MBC', 'brunchcafe', '2023-02-26')
    services.make_txt('MBC', 'brunchcafe', '2023-05-09')
    return 'test완료! html로 가서 결과를 테스트하세요'


###################################################################################


def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


########################
from flask import Flask, send_from_directory


# # brunchcafe라디오의 230226날짜로 고정된 화면이 보여진다.
# @auth.route('/brunchcafe/230226')
# def send_static():
#     return send_from_directory('../VisualRadio/static/html/', 'sub2.html')


########################


from flask import Blueprint
from flask import Flask, request, jsonify, send_file, render_template, request, make_response
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

# ------------------------------------- 서치 컨텐츠 라우트

@auth.route("/search/contents")
def search_contents() :
    search = request.args.get('search')
    data = services.search_contents(search)
    # logger.debug(f"[search] 검색 결과 {data}")
    return json.dumps(data)

# --------------------------------------------------------------------------------- 수집기
@auth.errorhandler(404)
@auth.route('/collector', methods=["POST"])
def collector():
    params = json.loads(request.get_data())
    broadcast = params['broadcast']
    time = params['start_time']
    logger.debug(f"{broadcast} {time}")
    result = services.collector_needs(broadcast, time)
    if result == None:
        # 응답 헤더와 상태 코드를 설정하여 에러 메시지 정보를 전달합니다.
        logger.debug(f"[collector error] 그러한 라디오({broadcast, time})가 DB에 없음")
        response = make_response(f"그러한 라디오({broadcast, time})가 DB에 없음", 404)
        return response
    return result

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

@auth.route("<string:broadcast>/<string:radio_name>/<string:radio_date>/get_process", methods=['GET'])
def get_process(broadcast, radio_name, radio_date):
    process = services.get_radio_process(broadcast, radio_name, radio_date)
    return jsonify(process)



# --------------------------------------------------------------------------------- admin페이지의 업로드 프로세스

@auth.route("/<string:broadcast>/<string:program_name>/<string:date>/check_wav", methods=['GET'])
def check_wav(broadcast, program_name, date):
    logger.debug("check_wav")
    path = f"VisualRadio/radio_storage/{broadcast}/{program_name}/{date}/raw.wav"
    if os.path.isfile(path):
        logger.debug("[업로드] wav가 이미 있나? 있다.")
        return jsonify({'wav':'true'})
    else:
        return jsonify({'wav':'false'})

@auth.route('/admin-update', methods=['POST'])
def admin_update():
    logger.debug(f"[업로드] 호출됨")
    broadcast = request.form.get('broadcast')
    program_name = request.form.get('program_name')
    date = request.form.get('date')
    guest_info = request.form.get('guest_info')
    try:
        audio_file = request.files.get('audio_file')
        audio_save(broadcast, program_name, date, audio_file)
    except:
        audio_file = None
    services.audio_save_db(broadcast, program_name, date)
    logger.debug(f"[업로드] 등록 완료: {broadcast}, {program_name}, {date}, {guest_info}")

    # 다른 프로세스를 백그라운드로 실행시키기
    logger.debug("[업로드] 음성처리 - 백그라운드로 시작")
    t = threading.Thread(target=process_audio_file, args=(broadcast, program_name, date))
    t.start()

    return jsonify({'message': 'Success'})


def process_audio_file(broadcast, name, date):
    services.split(broadcast, name, date)
    start_times = services.split_cnn(broadcast, name, date)
    services.stt(broadcast, name, date)
    services.before_script(broadcast, name, date, start_times, 'whisper')
    services.before_script(broadcast, name, date, start_times, 'google')
    services.make_script(broadcast, name, date)
    services.register_listener(broadcast, name, date)
    services.sum_wav_sections(broadcast, name, date)
    logger.debug("[업로드] 오디오 처리 완료")
    return "ok"

def audio_save(broadcast, program_name, date, audiofile):
    path = f"./VisualRadio/radio_storage/{broadcast}/{program_name}/{date}/"
    # 문제점: brunchcafe와 이석훈의브런치카페는 동일한 프로그램임. 추후 이 점 고려해야E 할 것임
    # DB에서 체크하는 방식으로 변경해야 함
    # if os.path.exists(path + '/raw.wav'):
        # logger.debug("[업로드] 이미 raw.wav가 존재함")
    # else:
    os.makedirs(path, exist_ok=True)
    audiofile.save(path + 'raw.wav')
    logger.debug(f"[업로드] raw.wav 저장 완료 - {broadcast} {program_name} {date}")
    return "ok"

# -------------------------------------------------------------------------------- 검색기능
@auth.route("/search")
def search_page():
    return render_template('search.html')

@auth.route("/search/program/<string:radio_name>")
def search_program(radio_name):
    # search = request.args.get('search')
    data = services.search_programs(radio_name)
    logger.debug(f"[프로그램 search] 검색 결과 {data}")
    
#     결과 형식 [{
# 	"broadcast": "Broadcast 1",
# 	"programs": [{
# 		"radio_name": "Radio Program 1",
# 		"img": "/static/main_imgs/Broadcast 1/Radio Program 1/main_img.jpeg"
# 		},
#             ...
#         ]
#     },
#     ...
# ]

    return json.dumps(data)

@auth.route("/search/listener/<string:code>")
def search_listener(code):
    # search = request.args.get('search')
    # data = services.search_listeners(code)
    
    data = [{
        'broadcast':'MBC FM4U',
        'radio_name': '이석훈의브런치카페',
        'radio_date':'2023-05-08',
        'preview_text':'안녕하세요. 저도 이석훈입니다. 라디오는 처음 들어보는데 이름이 같아서 한 번 보내봅니다.<br>라디오를 듣고 계시는 모든 분들 남은 오늘 하루도 파이팅입니다. \
            <br><br>드디어 대망의 날이 밝았습니다! 과연 보라돌이팀의 결과는~?<br>두구두구두구 12시간 뒤에 만나보시죠 :3'
    }]
    
    logger.debug(f"[청취자 search] 검색 결과 {data}")
    return json.dumps(data)


@auth.route("/search/contents/<string:search>")
def search_contentssearch(search) :
    # data = services.search_contents(search)
    data = [{
        'broadcast':'MBC FM4U',
        'radio_name': '이석훈의브런치카페',
        'radio_date':'2023-05-08',
        'contents':'보라돌이팀에서 졸업 프로젝트의 테스트 데이터로 이석훈의 브런치카페를 사용했다고 하는데요, 감사합니다.<br>남은 졸업 프로젝트도 파이팅하시길 쿤디가 응원합니다. \
            <br><br>신경준은 잠오는 중 ~<br>김예은, 진지원 쌩쌩하는 중 ^0^'
    }]
    logger.debug(f"[컨텐츠 search] 검색 결과 {data}")
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
    img_path = f"/static/main_imgs/{broadcast}/{radio_name}/main_img.jpeg"
    if not os.path.exists("./VisualRadio"+img_path):
        img_path = "/static/images/default_main.png"
    return json.dumps({'main_photo':img_path})

@auth.route('/<string:broadcast>/<string:radio_name>/<string:year>/<string:month>/all', methods=['GET'])
def load_month_info(broadcast, radio_name, year, month):
    return json.dumps(services.all_date_of(broadcast, radio_name, year, month))

@auth.route('/<string:radio_name>/radio_info', methods=['GET'])
def load_radio_info(radio_name):
    return json.dumps({'info':"음악과 함께 하는 다정한 시간 '이석훈의 브런치카페'<br>매일 오전 11부터 12시까지, MBC FM4U<br>쿤디랑 음악 들으면서 커피나 할까?<br>-<br>사연 보내기와 지난 방송 듣기는 아래 링크에서<br>litt.ly/mbc_brunchcafe<br>-<br>연출: 조민경 | 작가 : 서성은, 윤혜정"})

@auth.route('/contents', methods=['GET'])
def to_sub2():
    return render_template('sub2.html')



# --------------------------------------------------------------------------------- sub2


# 해당회차 청취자와 키워드 리턴!! (sub2의 사이드에 띄울 청취자 참여 바로가기?)
@auth.route('/<string:broadcast>/<string:name>/<string:date>/listeners', methods=['GET'])
def get_listeners(broadcast, name, date):
    result = services.get_this_listeners_keyword_time(broadcast, name, date)
    return json.dumps(result)

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


@auth.route('/<string:broadcast>/<string:radio_name>/<string:radio_date>/section', methods= ['GET'])
def load_index_info(broadcast, radio_name, radio_date) :
    section_time = [{'start_time' : "0:00.000",
                     'end_time'   : "0:06.000",
                     'type'       : 0},
                    {'start_time' : '14:16.000',
                     'end_time'   : '17:34.000',
                     'type'       : 1},
                    {'start_time' : "17:34.000",
                     'end_time'   : "59:45.000",
                     'type'       : 0}]
    # section_time = services.get_segment(broadcast, radio_name, radio_date) # 지금은 split_cnn이지만 나중에 다른 함수를 통해서 전체 구간을 던져줍니당
    # logger.debug(f"section_time : {section_time}")
    # 던져주는 형태는 [{start_time : ~, end_time : ~ , type : ~ }, ...]                                                                      
    return json.dumps(section_time)

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
    # try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # except:
        # logger.debug("[route.read_json_file] error!")
    return data


########################
from flask import Flask, send_from_directory


# # brunchcafe라디오의 230226날짜로 고정된 화면이 보여진다.
# @auth.route('/brunchcafe/230226')
# def send_static():
#     return send_from_directory('../VisualRadio/static/html/', 'sub2.html')


########################


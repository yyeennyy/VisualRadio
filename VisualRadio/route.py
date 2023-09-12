from flask import Blueprint
from flask import request, jsonify, send_file, render_template, request, make_response
from VisualRadio import app, db
import sys
sys.path.append('./VisualRadio')
import services
import json
import os
import threading
import traceback
import paragraph
import utils
import stt
import settings as settings
import time
from models import Process, Wav
from natsort import natsorted
import librosa
import numpy as np
import psutil
from numba import cuda
from numba.cuda.cudadrv.driver import CudaAPIError

auth = Blueprint('auth', __name__)


# 로거
from VisualRadio import CreateLogger
logger = CreateLogger("route")


class AudioHolderToArray:
    def __init__(self, broadcast, name, date):
        self.broadcast = broadcast
        self.name = name
        self.date = date
        self.splits = []
        self.tmps = [] # 5분 단위로 쪼갠 tmp음성
        self.mrs = [] # 5분 단위로 쪼갠 음성을 여기에 저장합니다.
        self.sr = 0
        self.sum = []
        self.sum_mrs = [] # 5분 단위로 쪼갠 음성을 합쳐줍니다.
    
    def set_audio_info(self):
        logger.debug("[AudioHolderToArray] setting..")
        path = f"{settings.STORAGE_PATH}/{self.broadcast}/{self.name}/{self.date}/split_wav/"
        file_names = natsorted(os.listdir(path))
        sum = []
        for name in file_names:
            path_ = os.path.join(path, name)
            y, sr = librosa.load(path_)
            self.splits.append([name[:-4], y])
            sum.append(y)
        self.sum = np.concatenate(sum)
        self.sr = sr    
        logger.debug("[AudioHolderToArray] done..")
    
    def set_sum(self, audio_arr):
        self.sum = audio_arr


# ------------------------------------- 서치 컨텐츠 라우트

@auth.route("/search/contents")
def search_contents() :
    search = request.args.get('search')
    data = services.search_contents(search)
    # logger.debug(f"[search] 검색 결과 {data}")
    return json.dumps(data)

# 임시 : 문단 테스트 용 검색창
@auth.route("/tmp_paragraph")
def tmp_paragraph() :
    return render_template('tmp_paragraph.html')

@auth.route("/tmp_paragraph/search/<string:searchInput>")
def tmp_search(searchInput):
    result = paragraph.tmp_search_paragraph(searchInput)
    logger.debug(f"[임시 기능] 키워드 '{searchInput}'로 '{len(result)}'개의 문단컨텐츠를 검색했습니다. {type(result)}")
    return jsonify(result)

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
    path = f"VisualRadio/radio_storage/{broadcast}/{program_name}/{date}/raw.wav"
    if os.path.isfile(path):
        # 빠른 업로드! ################
        # 1. 올바른 경로에 raw.wav 미리 넣어두기
        # 2. 해당 wav 데이터를 지우는 쿼리 실행
        with app.app_context():
            try:
                db.session.query(Wav).filter_by(broadcast=broadcast, radio_name=program_name, radio_date=date).delete()
                db.session.commit()
                logger.debug(f"[테스트모드ON] 기존 Wav 데이터를 삭제하고 재진행합니다!")
            except Exception as e:
                db.session.rollback()
                logger.debug(f"[테스트모드ON] 삭제쿼리 실패! {str(e)}")
            finally:
                db.session.close()
        ##############################
        logger.debug("[업로드] wav가 이미 존재한다! (이득!!!!)")
        return jsonify({'wav':'true'})
    else:
        logger.debug("[업로드] wav를 업로드합니다.")
        return jsonify({'wav':'false'})

@auth.route('/admin-update', methods=['POST'])
def admin_update():
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

    # 오디오 프로세스 백그라운드로 시작
    t = threading.Thread(target=process_audio_file, args=(broadcast, program_name, date))
    t.start()

    # 종료
    t.join(0.1)

    return jsonify({'message': 'Success'})



def bring_process(broadcast, name, date):
    process = db.session.query(Process).filter_by(broadcast=broadcast, radio_name=name, radio_date=date).first()
    if process:
        return process
    else:
        process = Process(broadcast, name, date)
        commit(process)
        return process
        
def commit(o):
    db.session.add(o)
    db.session.commit()
    return

# gpu 메모리 완전 정리
def clean_gpu():
    try:
        device = cuda.get_current_device()
        device.reset()
    except CudaAPIError:
        # CPU 모드에서는 정리할 것이 없다
        pass

def process_audio_file(broadcast, name, date):
    storage = f"{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/"
    utils.delete_ini_files(storage)
    audio_holder = AudioHolderToArray(broadcast, name, date)
    with app.app_context():
        process = bring_process(broadcast, name, date)
        process.set_raw()
        # (필요시 사용) 모든 Process 진행사항 지우기 
        # process.del_all()
        # commit(process)
        try:
            # start!
            s_time = time.time()

            # audio split
            if not process.split1_:
                services.split(broadcast, name, date, audio_holder)  # audio_holder: sum, splits, sr
                process.set_split1()
                process.set_sum()
                commit(process)
            else:
                logger.debug("[split1] pass")
            if len(audio_holder.splits) == 0 or len(audio_holder.sum) == 0 or audio_holder.sr == 0:
                audio_holder.set_audio_info()
                process.set_sum()
                commit(process)
            utils.rm(os.path.join(storage, "raw.wav"))
            
            if not process.split2_:
                # mr 제거
                services.remove_mr(audio_holder)
                clean_gpu()
                # cnn 분류기 돌리기
                services.split_cnn(broadcast, name, date, audio_holder)
                process.set_split2()
                clean_gpu()
                commit(process)
                
                # 사실 이 부분은 필요 없어지지만, 추후 array와 file을 둘 다 구현해주어 선택할 수 있게 할 예정이므로 남겨둡니다.
                utils.rm(os.path.join(storage, "mr_wav"))
                utils.rm(os.path.join(storage, "tmp_mr_wav"))
            else:
                logger.debug("[split2] pass")

            # text processing
            # - 기존: split한 wav파일의 duraion을 파악해서 time정보를 직접 계산했음
            # - 변동: wav테이블의 radio_section 컬럼 활용 -> 멘트 구간을 아니까, audio를 바로 슬라이싱 가능 & time 바로 적용
            if not process.all_stt_ or process.end_stt_ != process.all_stt_:
                ment_start_end = stt.get_stt_target(broadcast, name, date)
                process.set_all_stt(len(ment_start_end))
                process.del_stt()
                commit(process)

                stt.speech_to_text(broadcast, name, date, ment_start_end, audio_holder)
                clean_gpu()
                stt.make_script(broadcast, name, date)
                paragraph.compose_paragraph(broadcast, name, date) # stt가 재진행되면 문단구성도 새로 해야 함
                process.set_script()
                commit(process)

                # remove files
                utils.rm(os.path.join(storage, "stt"))
                utils.rm(os.path.join(storage, "raw_stt"))
                utils.rm(os.path.join(storage, "split_final"))
                utils.rm(os.path.join(storage, "split_wav"))
                utils.rm(os.path.join(storage, "stt_final"))
            else:
                logger.debug("[stt] pass")

            if process.error_ == 1:
                process.del_error()
            logger.debug("[업로드] 오디오 처리 완료")
            logger.debug(f"[업로드] 소요시간: {(time.time() - s_time)/60} 분")
            process = None

        except Exception as e:
            logger.debug(e)
            logger.debug("오류 발생!!!! 오디오 처리를 종료합니다.")
            process.set_error()
            commit(process)
            traceback_str = traceback.format_exc()
            logger.debug(traceback_str)

    audio_holder = None
    return "ok"

def audio_save(broadcast, program_name, date, audiofile):
    path = f"./VisualRadio/radio_storage/{broadcast}/{program_name}/{date}/"
    # 문제점: brunchcafe와 이석훈의브런치카페는 동일한 프로그램임. 추후 이 점 고려해야E 할 것임
    # DB에서 체크하는 방식으로 변경해야 함
    os.makedirs(path, exist_ok=True)
    audiofile.save(path + 'raw.wav')
    logger.debug(f"[업로드] saved - {broadcast} {program_name} {date}")
    return "ok"

# -------------------------------------------------------------------------------- 검색기능
@auth.route("/search")
def search_page():
    return render_template('search.html')

@auth.route("/search/program/<string:radio_name>")
def search_program(radio_name):
    # search = request.args.get('search')
    data = services.search_programs(radio_name)
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
    data = services.search_listeners(code)
    return json.dumps(data)


@auth.route("/search/contents/<string:search>")
def search_contentssearch(search) :
    data = services.search_contents(search)
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
    json_data = utils.read_json_file(path + '/result/script.json')
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
    data = utils.read_json_file(file_path)
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





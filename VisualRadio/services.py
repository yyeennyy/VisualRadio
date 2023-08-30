import os
from models import Wav, Radio, Process
import time
from sqlalchemy import text
import gc
from torch._C import *
import random
import settings as settings
import time
import utils
import wave
from split_module.split import start_split
from split_module.split2 import save_split, split_music
import threading
from datetime import datetime
from datetime import timedelta
import json

# logger
from VisualRadio import CreateLogger
logger = CreateLogger("services")

from VisualRadio import db, app



def extract_broadcast(script_path):
    parts = script_path.split("/")
    if len(parts) >= 4:
        return parts[3]  # "VisualRadio/radio_storage/broadcast/radio_name/radio_date/result/script.json"에서 'broadcast' 값 추출
    return None
def extract_radio_name(script_path):
    parts = script_path.split("/")
    if len(parts) >= 5:
        return parts[4]  
def extract_radio_date(script_path):
    parts = script_path.split("/")
    if len(parts) >= 6:
        return parts[5]
    return None



# --------------------------------------------- collector
def collector_needs(broadcast, time):
    with app.app_context():
        query = text("""
            SELECT CONCAT('{"radio_name":"', radio_name, '"', ',"record_len":', record_len, '}') 
            FROM radio 
            WHERE broadcast=""" +'"'+ broadcast +'"'+
            'AND start_time=' +'"'+ time +'"'
        )
        result = db.session.execute(query).first()
        if result == None:
            return None
        logger.debug(f"[test] {result[0]}")
        return json.dumps(result[0])

# --------------------------------------------- 검색 기능
def search_programs(search):
    query = text("""
        SELECT CONCAT(CONCAT('{"broadcast": "', broadcast, '", ', '"programs": [', GROUP_CONCAT(DISTINCT CONCAT('{"radio_name":"', radio_name, '"}') SEPARATOR ', '),']}'))
        FROM radio
        WHERE radio_name LIKE "%""" +search+ """%"
        GROUP BY broadcast;
    """)
    logger.debug(query)
    result = db.session.execute(query)
    dict_list = []
    for r in result:
        dict_list.append(json.loads(r[0]))

    for i in range(len(dict_list)):
        broadcast = dict_list[i]['broadcast']
        for j in dict_list[i]['programs']:
            radio_name = j['radio_name']
            img_path = f"/static/main_imgs/{broadcast}/{radio_name}/main_img.jpeg"
            if os.path.exists("./VisualRadio"+img_path):
                j['img'] = img_path
            else:
                j['img'] = "/static/images/default_main.png"
    json_data = json.dumps(dict_list, ensure_ascii=False)

    return json_data

# --------------------------------------------- 좋아요 기능
def like(bcc, name):
    with app.app_context():
        radio = Radio.query.filter_by(broadcast=bcc, radio_name=name).first()
        if radio:
            radio.like_cnt += 1
            cnt = radio.like_cnt
            db.session.add(radio)
            db.session.commit()
        else:
            logger.debug('해당하는 radio를 찾지 못했어요..!')

    return cnt
    
def unlike(bcc, name):
    with app.app_context():
        radio = Radio.query.filter_by(broadcast=bcc, radio_name=name).first()
        if(radio.like_cnt > 0):
            radio.like_cnt -= 1
        cnt = radio.like_cnt
        db.session.add(radio)
        db.session.commit()
    return cnt

def get_like_cnt(bcc, name):
    with app.app_context():
        radio = Radio.query.filter_by(broadcast=bcc, radio_name=name).first()
        if radio:
            return radio.like_cnt
        else:
            logger.debug('[오류 발생!] 해당하는 라디오를 찾지 못했습니다.')
            return None


# --------------------------------------------- main
def get_all_radio():
    with app.app_context():
        query = text("""
            SELECT CONCAT(CONCAT('{"broadcast": "', broadcast, '", ', '"programs": [', GROUP_CONCAT(DISTINCT CONCAT('{"radio_name":"', radio_name, '", "like_cnt":"', like_cnt, '"}') SEPARATOR ', '),']}'))
            FROM radio
            GROUP BY broadcast;
        """)
        result = db.session.execute(query)
        dict_list = []
        for r in result:
            # print(json.loads(r[0]))
            dict_list.append(json.loads((r[0])))

        for i in range(len(dict_list)):
            broadcast = dict_list[i]['broadcast']
            for j in dict_list[i]['programs']:
                radio_name = j['radio_name']
                img_path = f"/static/main_imgs/{broadcast}/{radio_name}/main_img.jpeg"
                if os.path.isfile("./VisualRadio" + img_path):
                    j['img'] = img_path
                else:
                    j['img'] = "/static/images/default_main.png"
        json_data = json.dumps(dict_list)
        return json_data


# --------------------------------------------- sub1
def all_date_of(broadcast, radio_name, year, month):
    with app.app_context():
        # month를 이용하여 시작일과 종료일 계산
        start_date = datetime.strptime(f'{year}-{month}-01', '%Y-%m-%d').date()
        # end_date = datetime.strptime(f'{year}-{month}-01', '%Y-%m-%d').replace(day=1, month=start_date.month+1) - timedelta(days=1)
        
        # end_date 계산 부분 : 12월 달력 구현이 안되는 건 여기가 문제였다.
        if start_date.month == 12:
            end_date = start_date.replace(day=31)  # 12월인 경우 마지막 날은 31일입니다.
        else:
            end_date = start_date.replace(day=1, month=start_date.month+1) - timedelta(days=1)
        # 여기까지

        
        # 해당 월의 데이터 조회
        targets = Wav.query.filter_by(broadcast=broadcast, radio_name=radio_name).filter(Wav.radio_date >= start_date, Wav.radio_date <= end_date).all()
        
        only_day_list = [wav.radio_date.split('-')[-1] for wav in targets]
        date_list = [{'date': day} for day in only_day_list]
        date_json = json.dumps(date_list)

        return date_json


# ---------------------------------------------- sub2 
# sub2에서 청취자 정보를 사이드에 띄우기 위해, 해당회차 listeners_list를 리턴한다.
def get_this_listeners_keyword_time(broadcast, name, date):
    with app.app_context():
        # keywords 테이블에서 해당 회차 청취자(code)와 (keyword) json으로 리턴 (그룹 바이 회차)
        query = text("""
            SELECT code, group_concat(keyword SEPARATOR ','), group_concat(time SEPARATOR ',')
            FROM keyword
            WHERE broadcast = '""" + broadcast + "' AND radio_name = '" + name + "' AND radio_date = '" + date 
            + "'GROUP BY code")

        result = db.session.execute(query).all()
        if result == None:
            return json.dumps({'keyword':'', 'code':'', 'time':''})
        answer = []
        ################# (임시: result_list에서 랜덤 2개 키워드 뽑아 '쉼표로 구분된 문자열로' 주기) #############
        for r in result:
            code = r[0]
            key_list = r[1].split(",")
            times = r[2].split(",")
            time = times[0]
            dict_object = json.loads(r[0])
            sample_size = 2
            if len(key_list) >= sample_size:
                random_key = random.sample(key_list, sample_size)
                logger.warn(f"랜덤키: {random_key}")
                joined_string = ', '.join(random_key)
                # 샘플링된 키들을 사용하는 코드 작성
            else:
                joined_string = ''.join(key_list)
            answer.append({'code':code, 'keyword':joined_string, 'time':time})
        ####################################################################################
        return json.dumps(answer, ensure_ascii=False)



# ----------------------------------------------------

def set_db():
    pass


def audio_save_db(broadcast, name, date):
    with app.app_context():
        # 일단 radio 테이블에 존재하지 않으면 추가해야 함
        radio = Radio.query.filter_by(broadcast=broadcast, radio_name=name).first()
        if not radio:
            logger.debug(f"[업로드] 새로운 라디오의 두두둥장!! {broadcast} {name}")
            radio = Radio(broadcast=broadcast, radio_name=name, start_time=None, record_len=0, like_cnt=0)

            db.session.add(radio)
        # wav 테이블에 해당회차 추가
        wav = Wav.query.filter_by(broadcast = broadcast, radio_name=name, radio_date=str(date)).first()
        if not wav:
            wav = Wav(radio_name=name, radio_date=date, broadcast=broadcast, radio_section="")
            db.session.add(wav)
        db.session.commit()
        
def get_segment(broadcast, name, date):
    with app.app_context():
    # 일단 radio 테이블에 존재하지 않으면 추가해야 함
        wav = Wav.query.filter_by(broadcast=broadcast, radio_name=name, radio_date = date).first()
        if not wav:
            logger.debug(f"오류!! 아직 해당 라디오의 구간 정보가 db에 저장되지 않았습니다. {name} {date}")
            return
        else:
            logger.debug(f"db에서 정보 로드 완료!!")
            res = wav.radio_section.replace("'", "\"")
            return json.loads(res)
        
from spleeter.separator import Separator
import shutil
import numpy as np
from natsort import natsorted

# 클래스로 뺐다 (진행시간 고려해서 spleeter 돌리려고)
class MrRemover:
    def __init__(self):
        self.is_running = False
        self.is_done = False
        self.thread = None
        self.separator = Separator('spleeter:2stems')

    def set_path(self, audio_path, tmp_mr_path):
        self.audio_path = audio_path
        self.tmp_mr_path = tmp_mr_path

    def start(self):
        self.is_running = True
        self.is_done = False
        self.start_time = time.time()  # 작업 시작시간 기록
        self.thread = threading.Thread(target=self.background_process)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=0.1)

    def background_process(self):
        while self.is_running:
            self.separator.separate_to_file(self.audio_path, self.tmp_mr_path) # 오래 걸리는 작업
            self.is_running = False
            self.is_done = True
            return

def remove_mr(broadcast, name, date, duration=int(600/2)):
    logger.debug("[mr제거] 시작")
    splited_path = utils.hash_splited_path(broadcast, name, date)
    section_wav_origin_names = natsorted(utils.ourlistdir(splited_path))

    tmp_path = utils.get_path(broadcast, name, date)+"tmp"
    if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
    
    for target_section in section_wav_origin_names:
        idx = 0
        test_path = os.path.join(splited_path, target_section) # 1차 splited한 sec_n.wav임
        sec_name = test_path.split("/")[-1].split(".")[0]
        logger.debug(f"[mr제거] {int(duration/60)}분 파일로 쪼개 저장중: {sec_name}")
        sec_name = test_path.split("/")[-1].split(".")[0] # sec_n으로 나옴.

        audio, sr = librosa.load(test_path)
        if(len(audio) > duration*sr):
            for i in range(0, len(audio)-duration*sr, duration*sr):
                seg_audio = audio[i : i+duration*sr]
                save_name = f"{tmp_path}/{sec_name}-{str(idx)}.wav"
                sf.write(save_name, seg_audio, sr)
                idx+= 1
            save_name = f"{tmp_path}/{sec_name}-{str(idx)}.wav"
            sf.write(save_name, audio[i+duration*sr:len(audio)], sr)
        else:
            save_name = f"{tmp_path}/{sec_name}-{str(idx)}.wav"
            sf.write(save_name, audio, sr)
    
    mr_path = utils.mr_splited_path(broadcast, name, date)
    tmp_mr_path = utils.tmp_mr_splited_path(broadcast, name, date)
    seg_list = utils.ourlistdir(tmp_path)

    #--------------------------------------------------------------
    mr_remover = MrRemover()
    for seg_mr in seg_list:
        logger.debug(f"[mr제거] {seg_mr} mr 제거중..")
        audio_path = os.path.join(tmp_path, seg_mr)

        mr_remover.set_path(audio_path, tmp_mr_path)
        mr_remover.start()
        try:
            while True:
                time.sleep(10)
                gc.collect()
                # 작업이 너무 오래 걸릴 경우 재시작 & 초기화
                # 설정해둔 시간값: duration / 2 : 쪼갠파일이 맥시멈 10분이면, 5분안에 처리되도록 의도
                if mr_remover.is_running and not mr_remover.is_done:
                    elapsed_time = time.time() - mr_remover.start_time
                    if elapsed_time > int(duration/2): 
                        logger.debug(f"[mr제거] {seg_mr} 오래 걸려서 재시작")
                        mr_remover.stop()
                        mr_remover = None
                        mr_remover = MrRemover()
                        mr_remover.set_path(audio_path, tmp_mr_path)
                        mr_remover.start()
                        gc.collect()
                elif not mr_remover.is_running and mr_remover.is_done:
                    break
        except:
            print("에러")

    mr_remover.stop()
    mr_remover = None
    gc.collect()
    #--------------------------------------------------------------

    # 디렉토리 자체 삭제
    shutil.rmtree(tmp_path)
    
    section_wav__names = natsorted(utils.ourlistdir(tmp_mr_path))
    for fname in section_wav__names:
        rname = fname.split("-")[0]
        logger.debug(f"[mr제거] 오디오 합치는 중.. {fname}")
        vocals = f"{tmp_mr_path}{fname}/vocals.wav"
        x, sr = librosa.load(vocals)
        for a in section_wav__names:
            if(fname == a):
                continue
            r2name = a.split("-")[0]
            if(r2name == rname):
                vocals2 = f"{tmp_mr_path}{a}/vocals.wav"
                y, sr = librosa.load(vocals2)
                x = np.concatenate((x, y),axis=0)
        direct = f"{mr_path}/{rname}.wav"
        if not os.path.exists(direct):
            sf.write(direct, x, sr)
    
    return
    
from natsort import natsorted 

def split_cnn(broadcast, name, date):
    logger.debug(f"[split_cnn] 구간정보(멘트/광고/노래) 파악 시작")

    model_path = settings.MODEL_PATH
    mr_path = utils.mr_splited_path(broadcast, name, date) # 1차 split 이후이므로 이 경로는 반드시 존재함
    section_mr_origin_names = natsorted(utils.ourlistdir(mr_path))
    section_start_time_summary = {}
    
    content_section_list = []
    for target_section in section_mr_origin_names:
        mr_seg_path = os.path.join(mr_path, target_section)
        output_path = os.path.join(utils.cnn_splited_path(broadcast, name, date), target_section[:-4])  # 2차 split 결과를 저장할 디렉토리 생성
        sec_path = os.path.join(utils.hash_splited_path(broadcast, name, date))
        ment_range, content_section, not_ment = save_split(model_path, output_path, mr_seg_path) # 2차 split 시작하기
        music_range = split_music(f"{sec_path}{target_section}", not_ment)
        
        total_duration = 0
        
        for filename in section_mr_origin_names:
            if(filename != target_section):
                file_path = utils.hash_splited_path(broadcast, name, date, filename)
                with wave.open(file_path, "r") as wav_file:
                    duration = wav_file.getnframes() / wav_file.getframerate()
                    total_duration += int(duration)
            else:
                break
        
        real_ment_range = [[total_duration + start_time_sec, total_duration + end_time_sec] for start_time_sec, end_time_sec in ment_range]    
        real_content_section = [[total_duration + start_time_sec, total_duration + end_time_sec] for start_time_sec, end_time_sec in content_section]


        for i, range_list in enumerate(real_content_section):
            start = range_list[0]
            end = range_list[1]
            if(start - 0.5 == int(start)):
                ms_start = "500"
            else:
                ms_start = "000"
            if(end - 0.5 == int(start)):
                ms_end = "500"
            else:
                ms_end = "000"
            
            start_time = f"{int(start) // 60}:{int(start) % 60:02d}.{ms_start}"
            end_time = f"{int(end) // 60}:{int(end) % 60:02d}.{ms_end}"
            
            if range_list in real_ment_range:
                item = {"start_time": str(start_time), "end_time": str(end_time), "type": 0}
            elif range_list in music_range:
                item = {"start_time": str(start_time), "end_time": str(end_time), "type": 1}
            else:
                item = {"start_time": str(start_time), "end_time": str(end_time), "type": 2}
            content_section_list.append(item)
        
        ment_start_times = []
        for range in real_ment_range:
            ment_start_times.append(range[0])

        section_start_time_summary[target_section] = ment_start_times
    with app.app_context():
        wav = Wav.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=str(date)).first()
        if wav:
            wav.radio_section = str(content_section_list)
            wav.start_times = json.dumps(section_start_time_summary)
        else:
            wav = Wav(broadcast = broadcast, radio_name = name, radio_date = date, radio_section = str(content_section_list), start_times=json.dumps(section_start_time_summary))
            db.session.add(wav)
        db.session.commit()

    return section_start_time_summary 


# ★
import os

def split(broadcast, name, date):
    song_path = utils.get_rawwavfile_path(broadcast, name, date)
    save_path = utils.hash_splited_path(broadcast, name, date)

    # 이미 분할 정보가 있는지 확인
    with app.app_context():
        process = Process.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=date).first()
        if not process:
            logger.debug("[split] radio가 등록되지 않음")
            return
        elif process.split1 != 0:
            logger.debug(f"[split] 기존 1차 split 정보 존재")
            return
        else:
            logger.debug("[split] start hashing!")

    # 가정: split을 위한 "고정음성"은 fix.db에 등록된 상태다.
    # 주어진 메인 음성을 split한다.

    start_time = time.time()
    start_split(song_path, name, save_path)

    end_time = time.time()
    os.makedirs(save_path, exist_ok=True)
    wav_files = [f for f in utils.ourlistdir(save_path) if f.endswith('.wav')]

    n = len(wav_files)
    logger.debug(f"[split] {n}분할됨 - {end_time-start_time:.2f} seconds")

    with app.app_context():
        wav = Wav.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=date).first()
        if not wav:
            wav = Wav(radio_name=name, radio_date=date, broadcast=broadcast)
            db.session.add(wav)
        db.session.commit()

    return 0



# ------------------------------------------------------------------------------------------ stt 이후 과정
import wave
import os
import json

import librosa
import librosa.util
import soundfile as sf
from natsort import natsorted


def sum_wav_sections(broadcast, name, date):
    # 각 파일의 input stream을
    # 하나의 output stream에 이어쓰기하여 sum.wav로 만들기
    src_path = utils.hash_splited_path(broadcast, name, date)
    dst_path = utils.get_path(broadcast, name, date) + "/sum.wav"
    src_files = natsorted(utils.ourlistdir(src_path))

    # input stream 리스트 생성 & wav파일의 파라미터 정보 가져오기
    input_streams = []
    for src in src_files:
        input_streams.append(wave.open(os.path.join(src_path, src), 'rb'))
    params = input_streams[0].getparams()

    # output stream을 wb로 열기 & 파라미터 세팅
    output_stream = wave.open(dst_path, 'wb')
    output_stream.setparams(params)

    # output stream에 input stream 내용 이어쓰기
    for input_stream in input_streams:
        output_stream.writeframes(input_stream.readframes(input_stream.getnframes()))
        input_stream.close()
    output_stream.close()
    
    logger.debug("[contents] sum.wav done.")
    
    return


###################################### 서비스 로직 ###################################
def get_all_radio_programs():
    with app.app_context():
        # wav 테이블의 pk값을 가져온다.
        # pk는 복합키로 있음
        all_wavs = Wav.query.all()
        all_wavs_json = [{'broadcast':wav.broadcast, 'radio_name': wav.radio_name, 'date': wav.radio_date} for wav in all_wavs]
    return all_wavs_json

def get_radio_process(broadcast, radio_name, radio_date):
    with app.app_context():
        # wav 테이블의 pk값을 가져온다.
        # pk는 복합키로 있음
        process = Process.query.filter(Process.broadcast==broadcast, Process.radio_name==radio_name, Process.radio_date==str(radio_date)).first()
        # if(process.split1 == 0):
        #     return 
        all = end = 0 
        all += 4+ process.all_stt
        end += process.split1 + process.split2 + process.end_stt + process.script + process.sum
        all_process = {'end': end, 'all': all, 'error':process.error}
    return all_process


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
# split2 경로가 바뀌었으므로, 수정해줌.
from split2.split2Ment import save_split, SplitMent
from split2.MrRemoverToArray import MrRemoverToArray, remove_mr_to_array
from split2.split2Music import split_music_new, split_music_origin
# from split2.MrRemoverToFile import MrRemoverToFile
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
        
        
# mr제거에 관한 부분을 클래스로 뺏으므로, 이 부분은 단순히 MrRemoverToArray를 호출하게만 했습니다.
def remove_mr(audio_holder):
    remove_mr_to_array(audio_holder)

import numpy as np
from natsort import natsorted 


def split_cnn(broadcast, name, date, audio_holder):
    logger.debug(f"[split_cnn] 구간정보(멘트/광고/노래) 파악 시작")

    ment_split_model_path = settings.MENT_MODEL_PATH
    
    # 기존에는 utils로 불러왔지만, 이제는 audio_holder가 거의 모든 것을 갖고있습니다.
    section_mr_origin_names = audio_holder.sum_mrs
    sec_wav_list = audio_holder.splits
    section_start_time_summary = {}
    
    content_section_list = []
    total_duration = 0
    
    # 모델을 사전에 로드하기 위해서, 클래스를 미리 선언해줍니다.
    split_ment = SplitMent()
    split_ment.set_model(ment_split_model_path)
    
    past_type = None
    idx = 0 # enumerate같은 놈
    for target_section, mr in section_mr_origin_names:
        wav = sec_wav_list[idx][1]
        sec_name = sec_wav_list[idx][0]
        idx += 1
        
        # 멘트 split에서 넘겨주는 인자들이 바뀌었습니다. 이 외에도, 불필요한게 몇개 있어보이지만 이 부분은 추후 수정하겠습니다.
        ment_range, content_section, not_ment = save_split(mr, sec_name, split_ment, audio_holder)
        logger.debug(f"[split_cnn] {target_section} split ment 끝, split_music 시작")
        
        # 광고 분류할 때 있어서도, 넘겨주는 인자가 바뀌게 됩니다. 현재는 기존 분류기를 사용하고, 예은 stt 처리가 완료되면 밑에 주석처리된 것을 사용한다.
        # music_range, ad_range = split_music_origin(wav, audio_holder.sr, not_ment)
        music_range, ad_range = split_music_new(audio_holder.jsons, not_ment)
        logger.debug(f"[split_cnn] {target_section} split_music 끝")
        
        # 현재 섹션의 재생 시간 계산
        # splits = audio_holder.splits
        # sr = audio_holder.sr
        # for split in splits:
        #     if split[0] == target_section[:-4]:
        #         duration = len(split[1]) / sr

        if target_section == section_mr_origin_names[-1]:
            break

        for i, range_list in enumerate(content_section):
            start = range_list[0]
            end = range_list[1]
            
            if range_list in ment_range:
                item = {"start_time": str(start), "end_time": str(end), "type": 0}
                past_type = 0
            elif range_list in music_range:
                item = {"start_time": str(start), "end_time": str(end), "type": 1}
                past_type = 0
            elif range_list in ad_range:
                item = {"start_time": str(start), "end_time": str(end), "type": 2}
                past_type = 0
            else:
                # 완전 처음 : 만약 whipser가 3초부터 시작하면, 0~3초는 그냥 멘트라고 생각.
                if(past_type is None):
                    item = {"start_time": str(start), "end_time": str(end), "type": 0}
                else:
                    item = {"start_time": str(start), "end_time": str(end), "type": past_type}
                    
            content_section_list.append(item)
        
        ment_start_times = []
        for range in ment_range:
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

def split(broadcast, name, date, audio_holder):
    song_path = utils.get_rawwavfile_path(broadcast, name, date)
    save_path = utils.hash_splited_path(broadcast, name, date)

    # 이미 분할 정보가 있는지 확인
    with app.app_context():
        process = Process.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=date).first()
        if not process:
            logger.debug("[split] radio의 Process가 등록되지 않음")
            return
        elif process.split1 != 0:
            logger.debug(f"[split] 기존 1차 split 정보 존재")
            return
        else:
            logger.debug("[split] start hashing!")

    # 가정: split을 위한 "고정음성"은 fix.db에 등록된 상태다.
    # 주어진 메인 음성을 split한다.

    start_time = time.time()
    start_split(song_path, name, save_path, audio_holder)
    sum_wav(audio_holder)

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


import librosa
import numpy as np
import soundfile as sf

def sum_wav(audio_holder):
    # 불러온 오디오 배열을 저장할 리스트
    splits = audio_holder.splits
    audio = []
    for split in splits:
        audio.append(split[1])
    concatenated_audio = np.concatenate(audio)
    concatenated_audio = concatenated_audio.astype('float32')
    audio_holder.set_sum = concatenated_audio
    sf.write(utils.get_path(audio_holder.broadcast, audio_holder.name, audio_holder.date) + "sum.wav", concatenated_audio, audio_holder.sr)
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

from googleapiclient.discovery import build

def get_music_link(music_name):
    # 내가 발급받은 키!!
    DEVELOPER_KEY = "AIzaSyBs569DvvdHwqmhdAomwc1qka6repVwgI0"
    YOUTUBE_API_SERVICE_NAME="youtube"
    YOUTUBE_API_VERSION="v3"
    youtube = build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    search_response = youtube.search().list(
        q = music_name+" M/V",
        order = "relevance",
        part = "snippet",
        maxResults = 30
        ).execute()

    base = 'https://www.youtube.com/watch?v='
    
    # API 응답에서 첫 번째 항목의 링크 가져오기
    link = search_response['items'][0]['id']['videoId']
    youtube_link = base+link
    
    return youtube_link
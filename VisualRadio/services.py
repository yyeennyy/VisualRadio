import os
from models import Wav, Radio, Listener, Process, Keyword
import time
# from flask import jsonify, Flask
from natsort import natsorted
from sqlalchemy import text
import gc
# import torch
from torch._C import *
import psutil
import random

# for split
from split_module.split import start_split

# for stt
# from google.oauth2 import service_account  # 구글 클라우드 인증설정
# from google.cloud import storage, speech_v1
import threading
from datetime import datetime
from datetime import timedelta
import json

# for audio process
import wave
from pydub import AudioSegment

# 로거
from VisualRadio import CreateLogger
logger = CreateLogger("우리가1등(^o^)b")

# sql
from sqlalchemy.exc import IntegrityError


from VisualRadio import db, app


# for cnn split
import os
import pandas as pd
import numpy as np
import librosa
import librosa.display
import tensorflow as tf
import soundfile as sf
from VisualRadio.split_module.split2 import save_split


# for etc
from konlpy.tag import Komoran
import math


# ----------- 옌 컨텐츠 검색 구현중 -----------
def search_contents(search_word):
    script_paths = search_scriptfile_under("VisualRadio/radio_storage", "result")
    search_result = []
    
    for script_path in script_paths:
        with open(script_path, 'r') as file:
            data = json.load(file)
            prev_txt = None
            next_txt = None
            current_txt = None
            for item in data:
                if 'txt' in item and search_word in item['txt']:
                    current_txt = item['txt']
                    # 이전, 현재, 다음 item['txt'] 값을 합쳐 contents 만들기
                    txt_list = []
                    if prev_txt:
                        txt_list.append(prev_txt)
                    txt_list.append(current_txt)
                    if next_txt:
                        txt_list.append(next_txt)
                    contents = " ".join(txt_list)

                    # script_path에서 변수 추출
                    broadcast = extract_broadcast(script_path)
                    radio_name = extract_radio_name(script_path)
                    radio_date = extract_radio_date(script_path)
                    # 결과를 딕셔너리로 생성하고 search_result에 추가
                    result = {
                        'broadcast': broadcast,
                        'radio_name': radio_name,
                        'radio_date': radio_date,
                        'contents': contents
                    }
                    search_result.append(result)
                # 이전, 현재, 다음 item['txt'] 값을 업데이트
                prev_txt = current_txt
                current_txt = next_txt
                next_txt = None
                # 다음 item이 존재하는 경우 다음 item['txt'] 값을 업데이트
                if item is not data[-1]:
                    next_txt = data[data.index(item) + 1]['txt']
                # 다음 반복 과정을 건너뛰는 경우
                if next_txt and search_word in next_txt:
                    continue
    return search_result

def search_scriptfile_under(basepath, target_dir):
    result_dir_path = None
    for root, dirs, files in os.walk(basepath):
        if target_dir in dirs:
            result_dir_path = os.path.join(root, target_dir)
            break
    # "script.json" 파일 확인
    script_path_list = []
    if result_dir_path:
        script_path = os.path.join(result_dir_path, "script.json")
        if os.path.isfile(script_path):
            print("script.json 파일 경로:", script_path)
            script_path_list.append(script_path)
        else:
            print("script.json 파일이 존재하지 않습니다.")
    else:
        print("result 디렉토리를 찾을 수 없습니다.")

    return script_path_list

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


def search_listeners(search):
    result = Listener.query.filter_by(code=search).all()
    info = []
    for r in result:
        data = {
            'broadcast':r.broadcast,
            'radio_name':r.radio_name,
            'radio_date':r.radio_date,
            'preview_text':r.preview_text
        }
        info.append(data)
    
    json_data = json.dumps(info, ensure_ascii=False)
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
            logger.debug('해당하는 radio를 찾지 못했어요.,!')

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
            logger.debug(f"[업로드] 새로운 라디오의 등장!! {broadcast} {name}")
            radio = Radio(broadcast=broadcast, radio_name=name, start_time=None, record_len=0, like_cnt=0)
            db.session.add(radio)
        # wav 테이블에 해당회차 추가
        wav = Wav.query.filter_by(broadcast = broadcast, radio_name=name, radio_date=str(date)).first()
        if not wav:
            wav = Wav(radio_name=name, radio_date=date, broadcast=broadcast, radio_section="")
            db.session.add(wav)
        process = Process.query.filter_by(broadcast = broadcast, radio_name=name, radio_date=str(date)).first()
        if process:
            # 기존 객체 수정
            process.raw = 1
            process.split1 = 0
            process.split2 = 0
            process.end_stt = 0
            process.all_stt = 0
            process.script = 0
            process.sum = 0
        else:
            process = Process(radio_name=name, radio_date=date, broadcast=broadcast, raw=1, split1=0, split2=0, end_stt=0,
                      all_stt=0, script=0, sum=0)
            db.session.add(process)
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

# ment_range = []
def split_cnn(broadcast, name, date):
    model_path = './VisualRadio/split_module/split_good_model.h5'
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    splited_path = path + "/split_wav" # 1차 split 이후이므로 이 경로는 반드시 존재함
    section_wav_origin_names = os.listdir(splited_path)
    section_start_time_summary = {}
    # real_content = []
    content_section_list = []
    for target_section in section_wav_origin_names:
        test_path = f"{splited_path}/{target_section}" # 1차 splited한 sec_n.wav임
        output_path = f"{path}/split_final/{target_section[:-4]}"  # 2차 split 결과를 저장할 디렉토리 생성
        os.makedirs(output_path, exist_ok=True)
        ment_range, content_section = save_split(test_path, model_path, output_path) # 2차 split 시작하기
        total_duration = 0
        
        for filename in os.listdir(splited_path+"/"):
            if(filename != target_section):
                file_path = os.path.join(splited_path+"/", filename)
                with wave.open(file_path, "r") as wav_file:
                    duration = wav_file.getnframes() / wav_file.getframerate()
                    total_duration += int(duration)
            else:
                break
        real_ment_range = [[total_duration + start_time_sec, total_duration + end_time_sec] for start_time_sec, end_time_sec in ment_range]    
        real_content_section = [[total_duration + start_time_sec, total_duration + end_time_sec] for start_time_sec, end_time_sec in content_section]
        # real_content.append(real_content_section)
        for i, range_list in enumerate(real_content_section):
            start = range_list[0]
            end = range_list[1]
            start_time = f"{start // 60}:{start % 60:02d}.000"
            end_time = f"{end // 60}:{end % 60:02d}.000"
            # logger.debug()
            if range_list in real_ment_range:
                item = {"start_time": str(start_time), "end_time": str(end_time), "type": 0}
            else:
                if(target_section == 'sec_2.wav' or target_section == 'sec_4.wav'): # 광고의 경우
                    item = {"start_time": str(start_time), "end_time": str(end_time), "type": 2}
                elif(target_section == 'sec_1.wav' or target_section == 'sec_3.wav'): # 1부, 2부의 경우
                    item = {"start_time": str(start_time), "end_time": str(end_time), "type": 1}
                else: # 오프닝의 경우
                    if(i+1 == len(real_content_section)): # 마지막 부분만 광고고 나머지는 다 노래!
                        item = {"start_time": str(start_time), "end_time": str(end_time), "type": 2}
                    else:
                        item = {"start_time": str(start_time), "end_time": str(end_time), "type": 1}
            content_section_list.append(item)
        
        ment_start_times = []
        for range in ment_range:
            start_time = format_time(range[0])
            ment_start_times.append(start_time)

        section_start_time_summary[target_section] = ment_start_times
    with app.app_context():
        process = Process.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=str(date)).first()
        if process:
            process.split2 = 1
        else:
            process = Process(broadcast=broadcast, radio_name = name, radio_date = date, raw=1, split1=1, split2=1,
                              end_stt=0, all_stt=0, script=0, sum=0)

            db.session.add(process)
        
        wav = Wav.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=str(date)).first()
        if wav:
            wav.radio_section = str(content_section_list)
        else:
            wav = Wav(broadcast = broadcast, radio_name = name, radio_date = date, radio_section = str(content_section_list))
            # logger.debug(str(content_section_list))
            db.session.add(wav)
        db.session.commit()

    return section_start_time_summary # 이 부분 수정해 바보야!!!!

# ★
def split(broadcast, name, date):
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    song_path = path + "/raw.wav"
    save_path = path + "/split_wav"
    os.makedirs(save_path, exist_ok=True)

    # 이미 분할 정보가 있는지 확인
    with app.app_context():
        process = Process.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=date).first()
        if not process:
            logger.debug("[split] 해당 라디오 데이터가 없습니다. 먼저 raw.wav를 등록하세요")
            return
        elif process.split1 != 0:
            logger.debug(f"[split] 분할 정보가 이미 있습니다")
            return
        else:
            logger.debug("[split] 분할 로직을 시작합니다")

    # 가정: split을 위한 "고정음성"은 fix.db에 등록된 상태다.
    # 주어진 메인 음성을 split한다.

    start_time = time.time()
    start_split(song_path, name, save_path)

    end_time = time.time()
    os.makedirs(save_path, exist_ok=True)
    wav_files = [f for f in os.listdir(save_path) if f.endswith('.wav')]

    n = len(wav_files)
    logger.debug(f"[split] {n}분할 처리 시간: {end_time - start_time} seconds")

    with app.app_context():
        wav = Wav.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=date).first()
        if not wav:
            wav = Wav(radio_name=name, radio_date=date, broadcast=broadcast)
            db.session.add(wav)
        process = Process.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=str(date)).first()
        if process:
            process.split1 = 1
        else:
            process = Process(broadcast=broadcast, radio_name = name, radio_date = date, raw=1, split1=1, split2=0,
                              end_stt=0, all_stt=0, script=0, sum=0)

            db.session.add(process)
        db.session.commit()
        
    return 0



# ------------------------------------------------------------------------------------------ stt 관련
import time
import json
import re
import wave
import whisper
from itertools import groupby
import threading
import gc
import queue
th_q = queue.Queue()
stt_count = 0
num_file = 0

def count_files(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        count += len(files)
    return count

def stt(broadcast, name, date):
    logger.debug("[stt] 시작")
    start_time = time.time()
    # 모든 sec_n.wav를 stt할 것이다
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"

    section_dir = f'{path}/split_final'       # 2차분할 결과로 반드시 존재
    section_list = os.listdir(section_dir)  

    global num_file
    num_file = count_files(section_dir)
    
    with app.app_context():
        process = Process.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=str(date)).first()
        if process:
            process.all_stt = num_file
        else:
            process = Process(broadcast=broadcast, radio_name = name, radio_date = date, raw=1, split1=1, split2=1,
                              end_stt=0, all_stt=num_file, script=0, sum=0)

            db.session.add(process)
        db.session.commit()
    
    for section_name in section_list: # 2차분할 결과 다루기 - section_name는 sec_1, sec_2 네임포맷의 디렉토리
        stt_targets_of_this_section = os.listdir(f"{section_dir}/{section_name}")  # sec_n의 2차분할 wav 리스트

        for section_mini in stt_targets_of_this_section: # section_mini는 2차분할 결과인, 작은 wav다
            logger.debug(f"[stt] stt할 파일 : {section_name}의 {section_mini} 파일 | 대기큐에 넣음")
            thread = threading.Thread(target=stt_proccess,
                                    args=(broadcast, name, date, section_name, section_mini))
            # th_q.put(thread)
            
        # th_q_fin = []
        # while not th_q.empty():
            # if len(threading.enumerate()) < 7:
                # time.sleep(random.uniform(0.1, 1))
                # if memory_usage("stt") < 0.75:
        logger.debug(f'{memory_usage("stt")*100}%')
        # this_th = th_q.get()
        logger.debug(f"{this_th.name} 시작! - 현재 실행중 쓰레드 개수 {len(threading.enumerate())}")
        this_th.start()
        th_q_fin.append(this_th)

        for thread in th_q_fin:
            thread.join()
        #     del thread

        end_time = time.time()
        logger.debug(f"[stt] {section_name} 완료 : 소요시간 {int((end_time-start_time)//60)}분 {int((end_time-start_time)%60)}초")
        gc.collect()
        
        # DB - stt를 True로 갱신
        with app.app_context():
            process = Process.query.filter_by(broadcast = broadcast, radio_name=name, radio_date=date).first()
            if not process:
                logger.debug(f"[stt] [오류] {broadcast} {name} {date} 가 있어야 하는데, DB에서 찾지 못함")


def stt_proccess(broadcast, name, date, section_name, section_mini):
    # 파라미터의 section_name은 1차분할 결과인 sec_1, sec_2와 같은 이름이다.
    # 파라미터의 section_mini는 2차분할 결과인 sec_n.wav와 같은 이름이다.

    # 경로 설정
    save_name = section_mini.replace(".wav", ".json")
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    src_path = f"{path}/split_final/{section_name}/{section_mini}" # stt 처리 타겟
    # stt결과 저장경로 설정하기
    os.makedirs(f"{path}/raw_stt/{section_name}", exist_ok=True)
    dst_path = f"{path}/raw_stt/{section_name}"
    # whisper stt 결과 얻기
    go_whisper_stt(src_path, dst_path + "/whisper", save_name)
    # google stt 결과 얻기
    interval = 10  # seconds
    go_fast_stt(src_path, dst_path + "/google", interval, save_name)
    
    global stt_count
    stt_count+=1
    
    with app.app_context():
        process = Process.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=str(date)).first()
        if process:
            process.end_stt = stt_count
        else:
            process = Process(broadcast=broadcast, radio_name = name, radio_date = date, raw=1, split1=1, split2=1,
                              end_stt=stt_count, all_stt=num_file, script=0, sum=0)

            db.session.add(process)
        db.session.commit()
    logger.debug(f"[stt] 끝끝! {section_name}/{section_mini}")
 
import speech_recognition as sr
from pydub import AudioSegment
def go_fast_stt(src_path, dst_path, interval, save_name):
    logger.debug(f"[stt] {dst_path}/{save_name} 진행 중")
    os.makedirs(dst_path, exist_ok=True)
    with wave.open(src_path, 'rb') as wav_file:
      sample_rate = wav_file.getframerate() 
      num_frames = wav_file.getnframes()  
      duration = num_frames / sample_rate  

    # 구간의 시작 및 끝 시간 계산
    start_time = 0
    end_time = start_time + interval * 1000  # 구간의 길이 (밀리초 단위)
    scripts = []
    r = sr.Recognizer()
    audio = AudioSegment.from_file(src_path)
    while end_time <= len(audio) or start_time < len(audio):
        try:
            # 해당 구간 임시파일
            audio_segment = audio[start_time:end_time]
            temp_file_path = "temp.wav"
            audio_segment.export(temp_file_path, format="wav")
            with sr.AudioFile(temp_file_path) as temp_audio_file:
                temp_audio_data = r.record(temp_audio_file)
                text = r.recognize_google(temp_audio_data, language='ko-KR')
                new_data = {f'time':format_time(start_time / 1000), 'txt':text}
                scripts.append(json.dumps(new_data, ensure_ascii=False))
        except Exception as e:
            pass
        start_time = end_time
        end_time += interval * 1000
    del r
    gc.collect()
    # 최종 data 저장하기
    data = {'end_time':format_time(duration), 'scripts':[json.loads(s) for s in scripts]}
    os.makedirs(f"{dst_path}", exist_ok=True)
    filename = f"{dst_path}/{save_name}"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    logger.debug(f"[stt] {dst_path}/{save_name} 진행 완료")
    return data


def go_whisper_stt(src_path, dst_path, save_name):
    os.makedirs(dst_path, exist_ok=True)
    filename = f"{dst_path}/{save_name}"
    device = "cpu"    #device = "cuda" if torch.cuda.is_available() else "cpu"
    language = "ko"

    # while True:
        # time.sleep(random.uniform(0.1, 1))
        # if memory_usage("stt") > 0.8:
            # continue
    logger.debug(f"[stt] {dst_path}/{save_name} 진행 중")
    model = whisper.load_model("base").to(device)
    results = model.transcribe(
        src_path, language=language, temperature=0.0, word_timestamps=True)
    del model
    gc.collect()
        # break

    # 스크립트 만들기
    endings = ['에요', '해요', '예요', '지요', '네요', '[?]{1}', '[가-힣]{1,2}시다', '[가-힣]{1,2}니다', '어요', '구요', '군요', '어요', '아요', '은요', '이요', '든요', '워요', '드리고요', '되죠', '하죠', '까요', '게요', '시죠', '거야', '잖아']
    scripts = []
    lines = []
    times = []
    for result in results['segments']:
        text = result['text']
        end_position = len(text)
        end_word = None
        for ending in endings:
            pattern = re.compile(ending)
            match = pattern.search(text)
            if match:
                now_position = match.start()
                if now_position < end_position:
                    end_position = now_position
                    end_word = ending
            else:
                pass
        # 시간 처리
        lines.append(text)
        times.append(result['start'])
        if end_word != None:
            scripts.append({'time':format_time(times[0]), 'txt':''.join(lines)})
            lines = []
            times = []

    # 결과물의 끝까지 종결 어미가 안나오는 경우이다
    # stt가 잘 안되는 경우, 동일 문장이 반복될 가능성이 높다 (whisper 특성)
    # groupby(lines)를 통해 동일문장을 하나만 반영
    unique_lines = [k for k, _ in groupby(lines)]
    if len(times) != 0:
        scripts.append({'time':format_time(times[0]), 'txt':''.join(unique_lines)})

    # 최종 script를 저장
    with wave.open(src_path, 'rb') as wav_file:
        sample_rate = wav_file.getframerate()
        num_frames = wav_file.getnframes()
        duration = num_frames / sample_rate
    data = {'end_time':format_time(duration), 'scripts':[s for s in scripts]}
    os.makedirs(f"{dst_path}", exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    logger.debug(f"[stt] {dst_path}/{save_name} 진행 완료")
    gc.collect()
    return data



# ------------------------------------------------------------------------------------------ stt 이후 과정


import wave
import shutil
import os
from natsort import natsorted
import json

def before_script(broadcast, name, date, start_times, stt_tool_name):
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    raw_stt = f'{path}/raw_stt'
    sec_n = os.listdir(raw_stt)
    duration_dict = get_duration_dict(broadcast, name, date)
    # sec_n
    for key in sec_n:
        sec_n_wav = f'{path}/split_wav/{key}.wav' #
        segments = natsorted(os.listdir(f'{raw_stt}/{key}/{stt_tool_name}'))
        time_start = start_times[f'{key}.wav']
        new_lines_sec_n = []
        for idx, segment in enumerate(segments): # 각각의 sec_i.json에 대해서..
            # print(segment) # sec_i.json
            with open(f'{raw_stt}/{key}/{stt_tool_name}/{segment}', 'r', encoding='utf-8') as f:
                data = json.loads(f.read())
            lines = data["scripts"]
            for line in lines:
                # 시간정보 업데이트
                new_lines_sec_n.append({'time':add_time(time_start[idx], line['time']), 'txt':line['txt']})
        
        # 최종 sec_n.json 생성 시작
        result_sec_n = {}

        result_sec_n['end_time'] = format_time(duration_dict[key])
        result_sec_n['scripts'] = new_lines_sec_n

        filename = f'{key}.json'
        # 파일 생성
        os.makedirs(f'{path}/stt_final/{stt_tool_name}', exist_ok=True)
        save_path = f'{path}/stt_final/{stt_tool_name}/{filename}'
        if os.path.exists(save_path):
            os.remove(save_path)
        with open(f'{save_path}', 'w') as f:
            f.write(json.dumps(result_sec_n, ensure_ascii=False))


# 최종 script.json을 생성한다.
# google과 whisper의 stt 결과를 모두 고려한다.
def make_script(broadcast, name, date):
    logger.debug("[make_script] script.json 생성중")
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"

    # google
    stt_dir = f'{path}/stt_final/google' # 반드시 존재
    stt_list = natsorted(os.listdir(stt_dir))
    targets = [os.path.join(stt_dir, name) for name in stt_list]
    os.makedirs(f"{path}/result/google", exist_ok=True)
    save_path = f"{path}/result/google/script.json"
    if os.path.exists(save_path):
        os.remove(save_path)
    with open(save_path, 'w') as f:
        f.write('')
    make_script_2(targets, save_path)

    # whisper
    stt_dir = f'{path}/stt_final/whisper' # 반드시 존재
    stt_list = natsorted(os.listdir(stt_dir))
    targets = [os.path.join(stt_dir, name) for name in stt_list]
    os.makedirs(f"{path}/result/whisper", exist_ok=True)
    save_path = f"{path}/result/whisper/script.json"
    if os.path.exists(save_path):
        os.remove(save_path)
    with open(save_path, 'w') as f:
        f.write('')
    section_start = make_script_2(targets, save_path)
    
    # 각 section의 stt결과를 합쳐 찐막 scripts를 만든다.
    correct_applicant(broadcast, name, date)
    logger.debug("[make_script] 사연자 보정 완료 => 최종 script.json 생성")
    
    global stt_count, num_file
    # DB - script를 True로 갱신
    with app.app_context():
        process = Process.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=str(date)).first()
        if process:
            process.script = 1
            db.session.add(process)
            db.session.commit()
        else:
            logger.debug(f"[make_script] [오류] {name} {date} 가 있어야 하는데, DB에서 찾지 못함")
    generate_images_by_section(broadcast, name, date, section_start)

# file_path에 있는 sections를 처리하여 save_path에 script.json을 저장한다.
def make_script_2(file_path, save_path):
    new_data = []
    section_start = []
    prev_end_time = "0:00.000"
    for file in file_path:
        section_start.append(prev_end_time)
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        scripts = data['scripts']
        for text in scripts:
            dic_data = {'time': add_time(prev_end_time, text['time']),
                        'txt': text['txt'].strip()}
            new_data.append(dic_data)
        prev_end_time = add_time(prev_end_time, data['end_time'])
    with open(save_path, 'a', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False)
    return section_start

import math
from datetime import datetime, timedelta
time_format = '%M:%S.%f'
number_dir = {'일': 1, '이': 2, '삼': 3, '사': 4, '오': 5, '호':5, '육': 6, '유': 6, '칠': 7, '팔': 8, '구': 9, '국':9, '군':9, '영': 0, '공':0, '하나': 1, '둘': 2, '셋': 3, '넷': 4, '다섯': 5, '여섯': 6, '일곱': 7, '여덟': 8, '아홉': 9}
def correct_applicant(broadcast, name, date):
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    g_path = f"{path}/result/google/script.json"
    w_path = f"{path}/result/whisper/script.json"
    save_path = f"{path}/result/script.json"

    # step1)
    # whisper 결과를 기준으로 google 결과를 매치
    # 텍스트 비교해보기
    with open(w_path, 'r', encoding='utf-8') as w:
        wdata = json.load(w)
    with open(g_path, 'r', encoding='utf-8') as g:
        gdata = json.load(g)

    g_text_prev = ""
    g_applicant = {}
    w_applicant = {}
    g_concat = []
    for w in wdata:
        w_time = w['time']
        w_dtime = convert_to_datetime(w_time)
        w_text = w['txt']
        for g in gdata:
            g_time = g['time'][:-4] + '.000'
            g_dtime = convert_to_datetime(g_time)
            g_text = g['txt']
            if w_dtime >= g_dtime: 
                g_concat.append(g_text)
            else:
                ' '.join(g_concat)
                g_concat = []
                break
        if g_text != g_text_prev:
            # print("\n┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────")
            # print("●", g_time, "[google]", g_text)
            if applicant_number(g_text) != None:
                # print("            사연자 : ", applicant_number(g_text))
                g_applicant[g_time] = applicant_number(g_text)
            # print("└───────────────────────────────────────────────────────────────────────────────────────────────────────────────")
            
        g_text_prev = g_text
        # print(w_time, ">>", w_text)
        if applicant_number(w_text) != None:
            # print("            사연자 : ", applicant_number(w_text))
            w_applicant[w_time] = applicant_number(w_text)

    # 이제부터 만들 결과물 : [멘트시간, 잘못된번호, 올바른번호]
    should_choice = {}
    this_is_true = {}
    tmp = set()
    for w_key in w_applicant:
        w_time = convert_to_datetime(w_key)
        w_element = w_applicant.get(w_key)
        for g_key in g_applicant:
            g_element = g_applicant.get(g_key)
            g_time = convert_to_datetime(g_key)
            # 기존: 겹치는 것만 고려했음
            if abs(w_time - g_time) <= timedelta(seconds=10):
                if w_element[1] != g_element[1]:
                    should_choice[w_key] = [w_element[1], g_element[1]]
                else:
                    this_is_true[w_key] = [w_element[0], w_element[1]]
                tmp.add(g_key)
        # 수정: whisper 단독도 true로 처리
        if w_key not in this_is_true:
            this_is_true[w_key] = [w_element[0], w_element[1]]

    for t in tmp:
        g_applicant.pop(t)

    google_alone = g_applicant
    logger.debug(f"[correct_applicant] 다음은 애매하여 처리하지 않았음 {should_choice}")
    logger.debug(f"[correct_applicant] 확실한 수정사항: {this_is_true}")
    # should_choice : 애매한 청취자 정보
    # this_is_true : 확실한 보정 정보
    # google_alone : 구글에만 탐지된 청취자 정보

    # google만 인식한 것은 whisper에서 어떨까?
    # +=10 범위에 숫자 인식 비슷하게 한 거 있으면, 그걸 후보군에 넣자.
    target_text = []   
    for g_key in google_alone:
        # print(g_key, google_alone.get(g_key))
        g_time = convert_to_datetime(g_key)
        for w in wdata:
            w_key = w['time']
            w_time = convert_to_datetime(w_key)
            if abs(g_time - w_time) < timedelta(seconds=10):
                # print(w_key, w['txt']) # target임
                target_text.append([w_key, w['txt'], google_alone.get(g_key)])
                # print('--------------')

    applicants_added_back = {}
    for text in target_text:
        w_key = text[0]
        w_text = text[1]
        g_hints = text[2]
        cnt = 0
        # logger.debug("--------- 청취자 찾는중 ----------")
        for hint in g_hints:
            contained = find_similar_strings(hint, w_text)
            if contained != None:
                cnt += 1
                # logger.debug(contained, "at", w_text)
            if cnt == len(g_hints):
                # logger.debug("---------- 최종 반영 ---------")
                # logger.debug(f"{w_key}에 {g_hints[1]} 청취자 정보 찾음")
                added = f"{w_text} :: ※ {g_hints[1]}청취자"
                logger.debug(added)
                applicants_added_back[w_key] = added
        # if target_text[-1] == text:
            # logger.debug("--------- 청취자 찾기 끝 ---------")
    logger.debug(f"added back: {applicants_added_back}")


    # 찾은 결과를 실제로 반영한다.
    # applicants_added_back : 정확히 대체하지 못함. 청취자번호를 뒤에 그냥 추가할 것임
    # this_is_true : 확실한 사연자 보정 정보
    result_data = []
    for w in wdata:
        if w['time'] in applicants_added_back:
            logger.debug(f"┌변환 전: {w['txt']}")
            w['txt'] = applicants_added_back.get(w['time']).strip()
            logger.debug(f"└변환 후: {w['txt']}")
        for w_key in this_is_true:
            if w['time'] == w_key:
                a = this_is_true.get(w_key)[0]
                b = this_is_true.get(w_key)[1]
                logger.debug(f"┌변환 전: {w['txt']}")
                w['txt'] = w['txt'].replace(a, b+"님")
                logger.debug(f"└변환 후: {w['txt']}")
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(wdata, f, ensure_ascii=False)
    logger.debug("[correct_applicant] 사연자 보정 완료")


# 만들어진 스크립트에서 청취자 찾기 
def register_listener(broadcast, radio_name, radio_date):
    script_file = f"./VisualRadio/radio_storage/{broadcast}/{radio_name}/{radio_date}/result/script.json"
    if not os.path.exists(script_file):
        logger.debug(f"[find_listner] 경고: 만들어진 script가 없음 {broadcast} {radio_name} {radio_date}")
    with open(script_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    regex = "(?<![0-9])(?<![0-9] )[0-9]{4}(?!년| 년)(?! [0-9])(?![0-9])" # 전화번호처럼 연속된 8자리(공백포함)는 인식하지 않는 정규표현식임
    listener_set = set()
    # preview_text_list = []
    for line in data:
        # 라인별 person_list 찾기
        # logger.debug(f"[ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ]lineㅡㅡㅡㅡ{line}")
        person_list = re.findall(regex, line['txt'])
        if len(person_list) == 0:
            continue
        # 찾았으
        listener_set = set.union(listener_set, person_list)
        # logger.debug(f"[ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ]listenre setㅡㅡㅡㅡ{listener_set}")

        # TODO: 개선하고 싶다. txt의 앞뒤를 가져오고 싶다. 그치만 지금은 한 문장에 대해서만 적용해보자.
        # for person in person_list:
            # preview_text_list.append({'code':person, 'txt':line['txt'], 'time':line['time']}) # 없어도 될듯? 각 person에 대해서 그떄그떄 처리해주면 되니까.
            # 현재회차의 해당 person에 대해 DB에 반영
        with app.app_context():
            try:
                for listener in listener_set:
                    text = line['txt']
                    db.session.add(Listener(broadcast=broadcast, radio_name=radio_name, radio_date=radio_date, code=listener, preview_text=text, time=line['time']))
                    # TODO: 현재 line['txt']에 대해 textrank적용 => keyword들 추출 => keyword DB테이블에 이 회차, 청취자, keyword 레코드 삽입하기!
                    ############### 키워드 추출 #################
                    # 유의: 키워드를 뽑으면서, 키워드가 없다면 아예 DB에 추가할 대상 문장이 아님.
                    # 전체 문장 내에서 핵심이 되는 키워드는? <= 일단 판단하지 말고, ㄱㅊ은 형태소는 다 넣자
                    keywords = extract_keywords(text)
                    stop_words = ['님', '하', '제가', '지', '고요', '저', '드', '들', '가', '보']
                    result = [keyword[0] for keyword in keywords if keyword[0] not in stop_words]
                    for r in result:
                        keyword = Keyword(broadcast=broadcast, radio_name=radio_name, radio_date=radio_date, code=listener, keyword=r, time=line['time'])
                        db.session.add(keyword)
                    db.session.commit()
            except IntegrityError as e:
                logger.debug("IntegrityError occurred............")
                ##########################################
    logger.debug(f"[find_listner] 청취자 업뎃완료: {listener_set} at {broadcast} {radio_name} {radio_date}")

def extract_keywords(sentence):
    komoran = Komoran()
    pos_tags = komoran.pos(sentence)
    keywords = [word for word in pos_tags if word[1]=='NNG' or word[1]=='XR' or word[1]=='NNP' or word[1]=='MAG']
    return keywords


import random
def generate_images_by_section(broadcast, name, date, section_start_list):
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    
    sec_img_data = []
    for idx, time in enumerate(section_start_list):
        dic_data = {
            'time': time,
            'img_url': f"https://picsum.photos/300/300/?image={random.randrange(0,100)}"
        }
        sec_img_data.append(dic_data)

    with open(f"{path}/result/section_image.json", 'w', encoding='utf-8') as f:
        json.dump(sec_img_data, f, ensure_ascii=False)
    logger.debug("[make_script] section_image.json 생성 완료!!!")
    
    



def add_time(time1, time2):
    time1 = datetime.strptime(time1, "%M:%S.%f").time()
    time2 = datetime.strptime(time2, "%M:%S.%f").time()

    delta = timedelta(hours=time1.hour, minutes=time1.minute, seconds=time1.second,
                               microseconds=time1.microsecond) + \
            timedelta(hours=time2.hour, minutes=time2.minute, seconds=time2.second,
                               microseconds=time2.microsecond)

    m, s = divmod(delta.seconds, 60)
    time_formatted = "{:d}:{:02d}.{:03d}".format(m, s, delta.microseconds // 1000)
    # print(time_formatted)
    return time_formatted

import librosa
import librosa.util as librosa_util
import soundfile as sf

def change_sr(path, sr_af):
    # name : 바꾸고자하는 파일의 경로입니다!
    # change_sr : 원하는 sr로 변경합니다! 들어오는 기본값은 44100으로 했습니다.
    # change_path : 바꾼 음성 파일을 저장할 경로입니다!
    
    # wave 파일 로드
    y, sr_or = librosa.load(path, sr=44100)
    
    # os.remove(path)

    # 원하는 sr 값으로 샘플링 주파수 변경
    y_resampled = librosa.resample(y, orig_sr=sr_or, target_sr=sr_af)

    # 변경된 wave 파일 저장
    sf.write(path, y_resampled, sr_af)


def sum_wav_sections(broadcast, name, date):
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    src_path = path + "/split_wav"
    dst_path = path + "/sum.wav"
    os.makedirs(src_path, exist_ok=True)
    src_files = natsorted(os.listdir(src_path))

    input_streams = []
    for src in src_files:
        input_streams.append(wave.open(src_path + "/" + src, 'rb'))
    # 첫 번째 입력 파일의 정보를 가져옵니다.
    params = input_streams[0].getparams()
    # 출력 파일을 열고 쓰기 모드로 처리합니다.
    output_stream = wave.open(dst_path, 'wb')
    # 출력 파일의 파라미터를 설정합니다.
    output_stream.setparams(params)
    # 입력 파일을 읽고 출력 파일에 작성합니다.
    for input_stream in input_streams:
        output_stream.writeframes(input_stream.readframes(input_stream.getnframes()))
    # 파일을 닫습니다.
    for input_stream in input_streams:
        input_stream.close()
    output_stream.close()
    
    # # sr을 줄이는 코드!!
    # change_sr(dst_path, 24000)
    
    global stt_count, num_file
    
    with app.app_context():
        process = Process.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=str(date)).first()
        if process:
            process.sum = 1
            db.session.add(process)
            db.session.commit()
        else:
            logger.debug(f"[make_script] [오류] {name} {date} 가 있어야 하는데, DB에서 찾지 못함")
    
    logger.debug("[contents] wav section들 이어붙이기 완료")
    



# 계획 없음 (멘트 섹션 찾기)
def find_contents(radio_name, date):
    pass


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
        all_process = {'end': end, 'all': all}
    return all_process


###################################### tools ###################################

def format_time(time_in_seconds):
    time_in_seconds = float(time_in_seconds)
    minutes, seconds = divmod(int(time_in_seconds), 60)
    milliseconds = int((time_in_seconds - int(time_in_seconds)) * 1000)
    return "{:d}:{:02d}.{:03d}".format(minutes, seconds, milliseconds) 

def applicant_number(text):
    if "문자" in text and ("샵" in text or "#" in text):
        return
    # 가능한 정규표현식이 최대한 매치되어야 하는 것이 관건
    number_re1 = r"(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1})(|,| |\.)?(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1}(?!에)(|,| |\.)?){2,3}(?![0-9])(?!씩|원))( )?[군|범|번]{1}( )?[님|림]{1})"
    number_re2 = r"(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1})(|,| |\.)?(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1}(?!에)(|,| |\.)?){2,3}(?![0-9])(?!씩|원))( )?[군|범|번]?( )?[님|림]{1})"
    number_re3 = r"(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1})(|,| |\.)?(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1}(?!에)(|,| |\.)?){2,3}(?![0-9])(?!씩|원))( )?[군|범|번]{1}( )?[님|림]?)"
    number_re4 = r"(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1})(|,| |\.)?(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1}(?!에)(|,| |\.)?){2,3}(?![0-9])(?!씩|원))( )?[군|범|번]?( )?[님|림]?)"
    reg_list = [number_re1, number_re2, number_re3, number_re4]
    for reg in reg_list:
        pattern = re.compile(reg)
        match = pattern.search(text)
        if match:
            raw = match.group().strip()
            if re.match(r'^\d{4}$', raw):
                return None
            fix = ''.join(str(number_dir.get(c, c)) for c in raw).replace(",","").replace(" ", "")
            fix = re.findall(r'\d{4}', fix)
            fix = ''.join(fix)
            if len(raw.replace(" ", "").replace(",", "")) >= 4:
                return [raw, fix]
            else:
                return None
    return None

# 사연자 찾기 도구들
def get_g_key_1(time_str):
    minutes, seconds = time_str.split(':')
    seconds = math.floor(float(seconds))
    time_str = f'{minutes}:{str(seconds).zfill(2)}.000'
    return time_str
def get_g_key_2(time_str):
    minutes, seconds = time_str.split(':')
    seconds = math.ceil(float(seconds))
    if seconds == 60:
        minutes = str(int(minutes) + 1)
        seconds = 0
    time_str = f'{minutes}:{str(seconds).zfill(2)}.000'
    return time_str
def get_ngrams(string, n):
    ngrams = []
    for i in range(len(string) - n + 1):
        ngram = string[i:i+n].strip()
        ngrams.append(ngram)
    return ngrams
def find_similar_strings(target, string):
    target_ngrams = get_ngrams(target, len(target)//2)
    contained = []
    finded = False
    for ngram in target_ngrams:
        if string.find(ngram) != -1:
            contained.append(ngram)
            finded = True
    if finded:
        return contained
    return None


def convert_to_datetime(time_str):
    minutes, seconds = time_str.split(':')
    seconds, milliseconds = seconds.split('.')
    
    hours = int(minutes) // 60
    minutes = int(minutes) % 60
    
    time_obj = datetime.min + timedelta(hours=hours, minutes=minutes, seconds=int(seconds), milliseconds=int(milliseconds))
    return time_obj

def get_duration_dict(broadcast, name, date):
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    wav_path = f'{path}/split_wav'
    stt_path = f'{path}/raw_stt'
    sorted = natsorted(os.listdir(wav_path))
    stts = natsorted(os.listdir(stt_path))

    duration_dict = {}
    all_duration = {}
    for key in sorted:
        key = key[:-4]
        wav_file = f'{wav_path}/{key}.wav'
        with wave.open(wav_file, 'rb') as f:
            sample_rate = f.getframerate() 
            num_frames = f.getnframes()  
            duration = num_frames / sample_rate
        all_duration[key] = duration

    # 기준 : stts
    # 이동 : sorted
    p = 0
    for idx, target in enumerate(stts):
        duration_dict[target] = 0
        while True:
            if sorted[p][:-4] != target:
                duration_dict[stts[idx-1]] += all_duration[sorted[p][:-4]]
                # print(stts[idx-1], "에 ", sorted[p][:-4], "저장")
                p += 1
                continue
            duration_dict[target] = all_duration[target]
            # print(sorted[p], target)
            p += 1
            break

    return duration_dict



def memory_usage(message: str = 'debug'):
    # current process RAM usage
    p = psutil.Process()
    rss = p.memory_info().rss / 2 ** 20 # Bytes to MB
    # print(f"[{message}] memory usage: {rss: 10.5f} MB |{type(rss)}| {(rss/5*8*1024)*100}%")
    return rss/(16*1024)
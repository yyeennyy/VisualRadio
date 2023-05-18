import os
from models import Wav
import glob
import time
import requests
import io
import sys
from flask import jsonify, Flask
from natsort import natsorted
from sqlalchemy import text

# for split
from split_module.split import start_split

# for stt
from google.oauth2 import service_account  # 구글 클라우드 인증설정
from google.cloud import storage, speech_v1
import threading
from datetime import datetime
from datetime import timedelta
import json

# for audio process
import wave
from pydub import AudioSegment

# 로거
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
#
file_handler = logging.FileHandler('my.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# logger = logging.getLogger(__name__)


from VisualRadio import db, app



# --------------------------------------------- main
def get_all_radio():
    with app.app_context():
            query = text("""
            SELECT CONCAT(CONCAT('{"broadcast": "', broadcast, '", ', '"programs": [', GROUP_CONCAT(DISTINCT CONCAT('{"radio_name":"', radio_name, '"}') SEPARATOR ', '),']}'))
            FROM wav
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
                    img_path = f"/static/{broadcast}/{radio_name}/main_img.png"
                    if os.path.exists(img_path):
                        j['img'] = img_path
                    else:
                        j['img'] = "/static/images/default_main.png"
            json_data = json.dumps(dict_list)
            return json_data


# --------------------------------------------- sub1
def all_date_of(radio_name, month):
    with app.app_context():
        logger.warn(month)
        # month를 이용하여 시작일과 종료일 계산
        start_date = datetime.strptime(f'2023-{month}-01', '%Y-%m-%d').date()
        end_date = datetime.strptime(f'2023-{month}-01', '%Y-%m-%d').replace(day=1, month=start_date.month+1) - timedelta(days=1)
        
        # 해당 월의 데이터 조회
        targets = Wav.query.filter_by(radio_name=radio_name).filter(Wav.radio_date >= start_date, Wav.radio_date <= end_date).all()
        
        only_day_list = [wav.radio_date.split('-')[-1] for wav in targets]
        date_list = [{'date': day} for day in only_day_list]
        date_json = json.dumps(date_list)
        logger.warning(date_json)

        return date_json


# ----------------------------------------------

def set_db():
    pass


def audio_save_db(broadcast, name, date):
    with app.app_context():
        wav = Wav.query.filter_by(radio_name=name, radio_date=str(date)).first()
        if wav:
            logger.debug(f"[업로드][경고] {name} {date}가 이미 있습니다 (덮어쓰기를 진행합니다)")
            # 기존 객체 수정
            wav.broadcast = broadcast
            wav.raw = True
            wav.section = 0
            wav.stt = False
            wav.script = False
            wav.contnets = False
        else:
            wav = Wav(radio_name=name, radio_date=date, broadcast=broadcast, raw=True, section=0, stt=False,
                        script=False, contents=False)
            db.session.add(wav)
        
        db.session.commit()


# ★
def split(broadcast, name, date):

    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    song_path = path + "/raw.wav"
    save_path = path + "/split_wav"
    os.makedirs(save_path, exist_ok=True)

    # 이미 분할 정보가 있는지 확인
    with app.app_context():
        # date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        wav = Wav.query.filter_by(radio_name=name, radio_date=str(date)).first()
        if not wav:
            logger.debug("[split] 해당 라디오 데이터가 없습니다. 먼저 raw.wav를 등록하세요")
            return
        if wav.section != 0:
            logger.debug(f"[split] 분할 정보가 이미 있습니다 - {wav.section} 분할")
            return
        else:
            logger.debug("[split] 분할 로직을 시작합니다")

    # 가정: split을 위한 "고정음성"은 fix.db에 등록된 상태다.
    # 주어진 메인 음성을 split한다.

    start_time = time.time()
    start_split(song_path, name, save_path)
    end_time = time.time()
    logger.debug(f"[split] 분할 처리 시간: {end_time - start_time} seconds")
    os.makedirs(save_path, exist_ok=True)
    wav_files = [f for f in os.listdir(save_path) if f.endswith('.wav')]

    n = len(wav_files)
    with app.app_context():
        wav = Wav.query.filter_by(radio_name=name, radio_date=date).first()
        if wav:
            wav.section = n
            db.session.commit()
        else:
            pass  # 해당 wav 모델 인스턴스가 없을 경우 처리
        
    


    return 0



# ------------------------------------------------------------------------------------------ stt 관련
import time
import json
import re
import wave
import whisper
from itertools import groupby
import threading

def stt(broadcast, name, date):
    logger.debug("[stt] 시작")
    start_time = time.time()
    # 모든 section 결과를 무조건 stt한다.
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    section_dir = f'{path}/split_wav'
    os.makedirs(section_dir, exist_ok=True)
    section_list = os.listdir(section_dir)
    # 섹션마다 stt 처리하기
    threads = []
    for section in section_list:
        logger.debug(f"[stt] stt할 파일 : {section}")
        # STT 수행
        thread = threading.Thread(target=run_quickstart,
                                  args=(broadcast, name, date, section))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    end_time = time.time()
    logger.debug(f"[stt] 완료 : 소요시간 {end_time-start_time}")
    # DB - stt를 True로 갱신
    with app.app_context():
        wav = Wav.query.filter_by(radio_name=name, radio_date=date).first()
        if wav:
            wav.stt = True
            db.session.add(wav)
            db.session.commit()
        else:
            logger.debug(f"[stt] [오류] {name} {date} 가 있어야 하는데, DB에서 찾지 못함")

def run_quickstart(broadcast, name, date, section):
    save_name = section.replace(".wav", ".json")
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    os.makedirs(f"{path}/split_wav", exist_ok=True)
    src_path = f"{path}/split_wav/{section}"                         #####################################
    dst_path = f"{path}/raw_stt"
    # ------------------------- 임시로 whisper 테스트를 sec_0에서 해보자
    if 'sec_0' in section:
        go_whisper_stt(src_path, dst_path, save_name)
    # --------------------------------------------- 기본 로직
    else: 
        interval = 10  # 구간의 길이 (초 단위)
        go_fast_stt(src_path, dst_path, interval, save_name)
        logger.debug(f"[stt] {save_name} 처리 완료")
    # ---------------------------------------------

import speech_recognition as sr
from pydub import AudioSegment
def go_fast_stt(src_path, dst_path, interval, save_name):
    logger.debug(f"[stt] {save_name} 는 SpeechRecognition 라이브러리로 진행합니다.")
    r = sr.Recognizer()
    # 음성 파일 로드 및 변환
    audio = AudioSegment.from_file(src_path)
    with wave.open(src_path, 'rb') as wav_file:
      sample_rate = wav_file.getframerate()  # 샘플 레이트
      num_frames = wav_file.getnframes()  # 프레임 수
      duration = num_frames / sample_rate  # 실제 음성 파일의 길이 (초 단위)
    # 구간의 시작 및 끝 시간 계산
    start_time = 0
    end_time = start_time + interval * 1000  # 구간의 길이 (밀리초 단위)
    scripts = []
    while end_time <= len(audio):
        try:
            # 구간 추출
            audio_segment = audio[start_time:end_time]
            # 추출된 구간을 임시 파일로 저장 (옵션)
            temp_file_path = "temp.wav"
            audio_segment.export(temp_file_path, format="wav")

            # 음성 인식 수행
            with sr.AudioFile(temp_file_path) as temp_audio_file:
                temp_audio_data = r.record(temp_audio_file)
                text = r.recognize_google(temp_audio_data, language='ko-KR')
                # 추출된 구간의 텍스트 출력 또는 원하는 로직 수행
                new_data = {f'time':format_time(start_time / 1000), 'txt':text}
                scripts.append(json.dumps(new_data, ensure_ascii=False))
        except Exception as e:
            if len(e) == 0:
                pass
            logger.warning(f"[stt] {save_name} 예외!!!! {e}")
            pass
        # 다음 구간으로 이동
        start_time = end_time
        end_time += interval * 1000
        
    # 마지막 구간 처리
    try:
        if start_time < len(audio):
            audio_segment = audio[start_time:]
            # 추출된 구간을 임시 파일로 저장 (옵션)
            temp_file_path = "temp.wav"
            audio_segment.export(temp_file_path, format="wav")
            # 음성 인식 수행
            with sr.AudioFile(temp_file_path) as temp_audio_file:
                temp_audio_data = r.record(temp_audio_file)
                text = r.recognize_google(temp_audio_data)
            # 추출된 구간의 텍스트 출력 또는 원하는 로직 수행
            # print(f"구간 {start_time / 1000} - {len(audio) / 1000}: {text}")
            new_data = {f'time':format_time(start_time / 1000), 'txt':text}
            scripts.append(json.dumps(new_data, ensure_ascii=False))
    except:
        pass
    # 최종 data
    data = {'end_time':format_time(duration), 'scripts':[json.loads(s) for s in scripts]}

    # 최종 data를 json으로 저장
    os.makedirs(f"{dst_path}", exist_ok=True)
    filename = f"{dst_path}/{save_name}"
    # if os.path.exists(filename):
    #     os.remove(filename)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    return data

def go_whisper_stt(src_path, dst_path, save_name):
    filename = f"{dst_path}/{save_name}"
    logger.debug(f"[whisper] {save_name}는 whisper로 처리합니다.")
    if os.path.exists(filename):
        logger.debug("[whisper] 처리 끝 (이미 존재)")
        return
    def show_progress(message):
        seconds = 0
        while is_running:
            print(f"[로딩] {message}... {seconds}초 지났어...♥")
            time.sleep(1)
            seconds += 2
        print(f"[로딩] {message}... 끝!!!!!!!!!!!!!!!!!!!!!!!!!")
    # device = "cuda" if torch.cuda.is_available() else "cpu"
    device = "cpu"
    language = "ko"
    model = whisper.load_model("base").to(device)
    # stt작업 하기 
    is_running = True
    thread = threading.Thread(target=show_progress, args=("whisper stt", ))
    thread.start()
    results = model.transcribe(
        src_path, language=language, temperature=0.0, word_timestamps=True)
    is_running = False
    thread.join()
    # 스크립트 만들기
    scripts = []
    lines = []
    times = []
    for result in results['segments']:
        text = result['text']
        endings = ['에요', '해요', '예요', '지요', '네요', '[?]{1}', '[가-힣]{1,2}시다', '[가-힣]{1,2}니다', '어요', '구요', '군요', '어요', '아요', '은요', '이요', '든요', '워요', '드리고요', '되죠', '하죠']
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
    # 결과물의 끝까지 종결 어미가 안나오는 경우
    unique_lines = [k for k, _ in groupby(lines)]
    if len(times) != 0:
        scripts.append({'time':format_time(times[0]), 'txt':''.join(unique_lines)})
    # 처리
    with wave.open(src_path, 'rb') as wav_file:
        sample_rate = wav_file.getframerate()
        num_frames = wav_file.getnframes()
        duration = num_frames / sample_rate
    data = {'end_time':format_time(duration), 'scripts':[s for s in scripts]}
    os.makedirs(f"{dst_path}", exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    logger.debug(f"[whisper] {save_name} 완료")
    return data





# def run_quickstart(broadcast, name, date, section, order):
#     import time
#     path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
#     os.makedirs(f"{path}/split_flac", exist_ok=True)
#     file_path = f"{path}/split_flac/{section}"
#     def flac_duration(audio_path):
#         audio = AudioSegment.from_file(audio_path, format="flac")
#         duration_micros = int(audio.duration_seconds * 1000000)
#         minutes, seconds = divmod(duration_micros / 1000000, 60)
#         microseconds = duration_micros % 1000
#         duration =  "{:d}:{:02d}.{:03d}".format(int(minutes), int(seconds), microseconds)
#         return duration
#     def format_time(time_in_seconds):
#         time_in_seconds = float(time_in_seconds)
#         minutes, seconds = divmod(int(time_in_seconds), 60)
#         milliseconds = int((time_in_seconds - int(time_in_seconds)) * 1000)
#         return "{:d}:{:02d}.{:03d}".format(minutes, seconds, milliseconds)
#     import whisper
#     device = "cpu"
#     language = "ko"
#     logger.debug("[stt] whisper 모델 불러오기")
#     model = whisper.load_model("tiny").to(device)
#     logger.debug("[stt] whisper의 transcribe시작")
#     results = model.transcribe(
#         file_path, language=language, temperature=0.0, word_timestamps=True
#     )
#     # 이미 json이 있으면 삭제 후 다시 stt 진행
#     os.makedirs(f"{path}/raw_stt", exist_ok=True)
#     filename = f"{path}/raw_stt/stt_%d.json" % (order)
#     if os.path.exists(filename):
#         os.remove(filename)
#     scripts = []
#     # stt 결과 가져오기 - text, time에 대한 json 만들기
#     logger.debug(f"[stt] stt_{order}.json 처리중")
#     scripts = []
#     for result in results['segments']:
#         new_data = {'time':format_time(str(result["start"])), 'txt':str(result['text'])}
#         scripts.append(json.dumps(new_data, ensure_ascii=False))
#     data = {'end_time':flac_duration(file_path), 'scripts':[json.loads(s) for s in scripts]}
#     with open(filename, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False)
#     logger.debug(f"[stt] stt_{order}.json 처리 완료")

# ★
# def stt(broadcast, name, date):
#     logger.debug("[stt] 시작")
#     start_time = time.time()
#     # 모든 section 결과를 무조건 stt한다.
#     path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
#     section_dir = f'{path}/split_flac'
#     os.makedirs(section_dir, exist_ok=True)
#     section_list = os.listdir(section_dir)
#     # STT 클라이언트 생성
#     project_id = 'RadioProject'
#     credentials = service_account.Credentials.from_service_account_file('./VisualRadio/credentials.json')
#     client = speech_v1.SpeechClient(credentials=credentials)
#     storage_client = storage.Client(project=project_id, credentials=credentials)
#     # 섹션마다 stt 처리하기
#     threads = []
#     for order, section in enumerate(section_list):
#         logger.debug(f"[stt] stt할 파일 : {section}")
#         # STT 수행
#         thread = threading.Thread(target=run_quickstart,
#                                   args=(broadcast, name, date, section, client, storage_client, order))
#         threads.append(thread)
#         thread.start()
#     for thread in threads:
#         thread.join()
#     end_time = time.time()
#     logger.debug(f"[stt] 완료 : 소요시간 {end_time-start_time}")
#     # DB - stt를 True로 갱신
#     with app.app_context():
#         wav = Wav.query.filter_by(radio_name=name, radio_date=date).first()
#         if wav:
#             wav.stt = True
#             db.session.add(wav)
#             db.session.commit()
#         else:
#             logger.debug(f"[stt] [오류] {name} {date} 가 있어야 하는데, DB에서 찾지 못함")
# def run_quickstart(broadcast, name, date, section, client, storage_client, order):
#     import time
#     from google.api_core.exceptions import ServiceUnavailable
#     # 참고: wav가 아닌 flac 기반 stt 진행
#     path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
#     os.makedirs(f"{path}/split_flac", exist_ok=True)
#     file_path = f"{path}/split_flac/{section}"
#     bucket_name = 'radio_bucket'
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(section)
#     blob.upload_from_filename(file_path)
#     storage_file_path = f'gs://{bucket_name}/{blob.name}'
#     audio = speech_v1.RecognitionAudio(uri=storage_file_path)
#     config = speech_v1.RecognitionConfig(
#         language_code='ko-KR',
#     )
#     operation = client.long_running_recognize(config=config, audio=audio)
#     logger.debug('[stt] response 받아오기 시작')
#     response = operation.result(timeout=999999)
#     logger.debug('[stt] response 받아옴')

#     results = response.results
    
#     start_time_delta = timedelta(hours=0, minutes=0, seconds=0, microseconds=0)
#     m, s = divmod(start_time_delta.seconds, 60)
#     start_time_formatted = "{:d}:{:02d}.{:03d}".format(m, s, start_time_delta.microseconds)
#     # 이미 json이 있으면 삭제 후 다시 stt 진행
#     os.makedirs(f"{path}/raw_stt", exist_ok=True)
#     filename = f"{path}/raw_stt/stt_%d.json" % (order)
#     if os.path.exists(filename):
#         os.remove(filename)
#     scripts = []
#     # stt 결과 가져오기 - text, time에 대한 json 만들기
#     logger.debug(f"[stt] stt_{order}.json 처리중")
#     for result in results:
#         # 각 음성 인식 결과에서 가장 가능성이 높은 대안을 사용
#         alternative = result.alternatives[0]
#         # with open("./stt_result_google.json", 'w', encoding='utf-8') as f:
#         #     json.dumps(alternative, f, ensure_ascii=False)
#         new_data = {'time': start_time_formatted, 'txt': alternative.transcript}
#         scripts.append(json.dumps(new_data, ensure_ascii=False))
#         # start time 갱신
#         start_time_delta = result.result_end_time
#         m, s = divmod(start_time_delta.seconds, 60)
#         start_time_formatted = "{:d}:{:02d}.{:03d}".format(m, s, start_time_delta.microseconds)

#     end_time = str(get_flac_duration(file_path))
#     data = {'end_time': end_time, 'scripts': [json.loads(s) for s in scripts]}
#     with open(filename, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False)
#     logger.debug(f"[stt] stt_{order}.json 처리 완료")

# def get_flac_duration(filepath):
#     audio = AudioSegment.from_file(filepath, format="flac")
#     duration_micros = int(audio.duration_seconds * 1000000)
#     minutes, seconds = divmod(duration_micros / 1000000, 60)
#     microseconds = duration_micros % 1000
#     return "{:d}:{:02d}.{:03d}".format(int(minutes), int(seconds), microseconds)

# def get_request_url_raw(radio_name, date):
#     url = "http://localhost:5000/%s/%s/wave" % (radio_name, date)
#     logger.debug(f"요청 경로:  {url}")
#     response = requests.get(url)
#     if response.status_code == 200:
#         return io.BytesIO(response.content)


# def get_request_url_fixed(radio_name, date, filename):
#     url = "http://localhost:5000/%s/%s/fixed/%s" % (radio_name, date, filename)
#     logger.debug(f"요청 경로:  {url}")
#     response = requests.get(url)
#     if response.status_code == 200:
#         return io.BytesIO(response.content)


# wav to flac (google stt 권장 포맷)
# def wavToFlac(broadcast, name, date):
#     path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
#     wav_loc = f"{path}/split_wav"
#     flac_loc = f"{path}/split_flac"
#     os.makedirs(flac_loc, exist_ok=True)
#     wav_path = get_file_path_list(wav_loc)
#     for order, wav in enumerate(wav_path):
#         song = AudioSegment.from_wav(wav)
#         song.export(flac_loc + "/sec_%d.flac" % (order), format="flac")
#     logger.debug("-- stt를 하기 위해 wav를 flac으로 변환했습니다 --")


# ------------------------------------------------------------------------------------------ stt 이후 과정

# 최종 script.json을 생성한다
def make_txt(broadcast, name, date):
    logger.debug("[make_txt] 전체 script.json 생성 시작")
    # stt_n.json 각각을 처리
    # end_time을 고려하여 제작
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"

    stt_dir = f'{path}/raw_stt'
    os.makedirs(stt_dir, exist_ok=True)
    stt_list = natsorted(os.listdir(stt_dir))
    file_path = [os.path.join(stt_dir, name) for name in stt_list]

    os.makedirs(f"{path}/result", exist_ok=True)
    script_path = f"{path}/result/script.json"
    # 파일이 존재하면 삭제
    if os.path.exists(script_path):
        os.remove(script_path)
    # 빈 파일 생성
    with open(script_path, 'w') as f:
        f.write('')
    new_data = []
    section_start = []
    prev_end_time = "0:00.000"
    for file in file_path:
        logger.debug(f"[script] 합치는 중 - {file}")
        section_start.append(prev_end_time)
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        scripts = data['scripts']
        for text in scripts:
            dic_data = {'time': add_time(prev_end_time, text['time']),
                        'txt': text['txt'].strip()}
            new_data.append(dic_data)
        prev_end_time = add_time(prev_end_time, data['end_time'])

    with open(script_path, 'a', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False)

    # DB - script를 True로 갱신
    with app.app_context():
        wav = Wav.query.filter_by(radio_name=name, radio_date=date).first()
        if wav:
            wav.script = True
            db.session.add(wav)
            db.session.commit()
        else:
            logger.debug(f"[make_txt] [오류] {name} {date} 가 있어야 하는데, DB에서 찾지 못함")

    logger.debug("[make_txt] script.json 생성 완료!!!")
    generate_images_by_section(broadcast, name, date, section_start)

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
    logger.debug("[make_txt] section_image.json 생성 완료!!!")


def add_time(time1, time2):
    time1 = datetime.strptime(time1, "%M:%S.%f").time()
    time2 = datetime.strptime(time2, "%M:%S.%f").time()

    delta = timedelta(hours=time1.hour, minutes=time1.minute, seconds=time1.second,
                               microseconds=time1.microsecond) + \
            timedelta(hours=time2.hour, minutes=time2.minute, seconds=time2.second,
                               microseconds=time2.microsecond)

    m, s = divmod(delta.seconds, 60)
    time_formatted = "{:d}:{:02d}.{:03d}".format(m, s, delta.microseconds // 1000)
    print(time_formatted)
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


###################################### tools ###################################

def format_time(time_in_seconds):
    time_in_seconds = float(time_in_seconds)
    minutes, seconds = divmod(int(time_in_seconds), 60)
    milliseconds = int((time_in_seconds - int(time_in_seconds)) * 1000)
    return "{:d}:{:02d}.{:03d}".format(minutes, seconds, milliseconds)



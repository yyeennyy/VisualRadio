import os
from models import db, Wav
import glob
import time
import requests
import io
import sys
from app import app # 문제

# for split
import split_module.split as splitpath

# for stt
import speech_recognition as sr
from google.oauth2 import service_account  # 구글 클라우드 인증설정
from google.cloud import storage, speech_v1
from google.oauth2 import service_account
import threading
from datetime import datetime
from datetime import timedelta
import json

# for audio process
import wave
from pydub import AudioSegment

# logging 미사용 상태임
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


storage_path = ".\\VisualRadio\\radio_storage"



def setup_db():
    pass


def audio_save_db(broadcast, name, date):
    with app.app_context():
        wav = Wav.query.filter_by(radio_name=name, radio_date=str(date)).first()
        if not wav:
            wav = Wav(radio_name=name, radio_date=date, broadcast=broadcast, raw=True, section=0, stt=False,
                      script=False, contnets=False, done=False)
            db.session.add(wav)
            db.session.commit()
        else:
            print(f"[업로드][경고] {name} {date}가 이미 있습니다")


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
            print("[split] 해당 라디오 데이터가 없습니다. 먼저 raw.wav를 등록하세요")
            return
        if wav.section != 0:
            print("[split] 분할 정보가 이미 있습니다 - %d 분할" % wav.section)
            return
        else:
            print("[split] 분할 로직을 시작합니다")

    # 가정: split을 위한 "고정음성"은 fix.db에 등록된 상태다.
    # 주어진 메인 음성을 split한다.

    start_time = time.time()
    splitpath.split(song_path, name, save_path)
    end_time = time.time()
    print("[split] 분할 처리 시간: ", end_time - start_time, "seconds")
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


def get_request_url_raw(radio_name, date):
    url = "http://localhost:5000/%s/%s/wave" % (radio_name, date)
    print("요청 경로: " + url)
    response = requests.get(url)
    if response.status_code == 200:
        return io.BytesIO(response.content)


def get_request_url_fixed(radio_name, date, filename):
    url = "http://localhost:5000/%s/%s/fixed/%s" % (radio_name, date, filename)
    print("요청 경로: " + url)
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        return io.BytesIO(response.content)


# wav to flac (google stt 권장 포맷)
def wavToFlac(broadcast, name, date):
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    wav_loc = f"{path}/split_wav"
    flac_loc = f"{path}/split_flac"
    os.makedirs(flac_loc, exist_ok=True)
    wav_path = get_file_path_list(wav_loc)
    for order, wav in enumerate(wav_path):
        song = AudioSegment.from_wav(wav)
        song.export(flac_loc + "/sec_%d.flac" % (order), format="flac")
    print("-- stt를 하기 위해 wav를 flac으로 변환했습니다 --")


# ★
def stt(broadcast, name, date):
    print("[stt] 시작")
    start_time = time.time()
    # start_time 
    # 모든 section 결과를 무조건 stt한다.
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    section_dir = f'{path}/split_flac'
    os.makedirs(section_dir, exist_ok=True)
    section_list = os.listdir(section_dir)

    # STT 클라이언트 생성
    project_id = 'RadioProject'
    credentials = service_account.Credentials.from_service_account_file('D:\JP\Server\VisualRadio\credentials.json')
    client = speech_v1.SpeechClient(credentials=credentials)
    storage_client = storage.Client(project=project_id, credentials=credentials)

    # 섹션마다 stt 처리하기
    threads = []
    for order, section in enumerate(section_list):
        print("[stt] stt할 파일 : " + section)
        # STT 수행
        thread = threading.Thread(target=run_quickstart,
                                  args=(broadcast, name, date, section, client, storage_client, order))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    print("[stt] 완료 : 소요시간", end_time-start_time)

    # DB - stt를 True로 갱신
    with app.app_context():
        wav = Wav.query.filter_by(radio_name=name, radio_date=date).first()
        if wav:
            wav.stt = True
            db.session.add(wav)
            db.session.commit()
        else:
            print(f"[stt] [오류] {name} {date} 가 있어야 하는데, DB에서 찾지 못함")


def run_quickstart(broadcast, name, date, section, client, storage_client, order):
    # 참고: wav가 아닌 flac 기반 stt 진행
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    os.makedirs(f"{path}/split_flac", exist_ok=True)
    file_path = f"{path}/split_flac/{section}"
    bucket_name = 'radio_bucket'

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(section)
    blob.upload_from_filename(file_path)
    storage_file_path = f'gs://{bucket_name}/{blob.name}'

    audio = speech_v1.RecognitionAudio(uri=storage_file_path)
    config = speech_v1.RecognitionConfig(
        language_code='ko-KR',
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=999999)

    results = response.results

    start_time_delta = timedelta(hours=0, minutes=0, seconds=0, microseconds=0)
    m, s = divmod(start_time_delta.seconds, 60)
    start_time_formatted = "{:d}:{:02d}.{:03d}".format(m, s, start_time_delta.microseconds)

    # 이미 json이 있으면 삭제 후 다시 stt 진행
    os.makedirs(f"{path}/raw_stt", exist_ok=True)
    filename = f"{path}/raw_stt/stt_%d.json" % (order)
    if os.path.exists(filename):
        os.remove(filename)

    scripts = []
    # stt 결과 가져오기 - text, time에 대한 json 만들기
    print("[stt] stt_%d.json 처리중" % (order))
    for result in results:
        # 각 음성 인식 결과에서 가장 가능성이 높은 대안을 사용
        alternative = result.alternatives[0]
        new_data = {'time': start_time_formatted, 'txt': alternative.transcript}

        scripts.append(json.dumps(new_data, ensure_ascii=False))

        # start time 갱신
        start_time_delta = result.result_end_time
        m, s = divmod(start_time_delta.seconds, 60)
        start_time_formatted = "{:d}:{:02d}.{:03d}".format(m, s, start_time_delta.microseconds)

    end_time = str(get_flac_duration(file_path))
    data = {'end_time': end_time, 'scripts': [json.loads(s) for s in scripts]}
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    print("[stt] stt_%d.json 처리 완료" % (order))


def get_flac_duration(filepath):
    audio = AudioSegment.from_file(filepath, format="flac")
    duration_micros = int(audio.duration_seconds * 1000000)
    minutes, seconds = divmod(duration_micros / 1000000, 60)
    microseconds = duration_micros % 1000
    return "{:d}:{:02d}.{:03d}".format(int(minutes), int(seconds), microseconds)


# 최종 script.json을 생성한다
def make_txt(broadcast, name, date):
    print("[make_txt] 전체 script.json 생성 시작")
    # stt_n.json 각각을 처리
    # end_time을 고려하여 제작
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"

    stt_dir = f'{storage_path}/raw_stt'
    os.makedirs(stt_dir, exist_ok=True)
    stt_list = os.listdir(stt_dir)
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
            print(f"[make_txt] [오류] {name} {date} 가 있어야 하는데, DB에서 찾지 못함")

    print("[make_txt] script.json 생성 완료!!!")


def generate_images_by_section(broadcast, name, date, section_start_list):
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"

    img_url_1 = "https://img.hankyung.com/photo/202203/01.29353881.1-1200x.jpg"
    img_url_2 = "https://pbs.twimg.com/ext_tw_video_thumb/1514084683608309764/pu/img/1ihM-03RUgNtJqcs.jpg"
    img_url_3 = "https://static.inews24.com/v1/4815fc2c7e522d.jpg"
    img_url_4 = "https://cdn.litt.ly/images/NEpLQ6zpkVRqKo0EzVy3kg1wzlR68XYL?s=1200x630&m=inside"

    sec_img_data = []
    img_url_data = [img_url_1, img_url_2, img_url_3, img_url_4]

    for idx, time in enumerate(section_start_list):
        dic_data = {
            'time': time,
            'img_url': img_url_data[idx]
        }
        sec_img_data.append(dic_data)

    with open(f"{path}/result/section_image.json", 'w', encoding='utf-8') as f:
        json.dump(sec_img_data, f, ensure_ascii=False)
    print("[make_txt] section_image.json 생성 완료!!!")


def add_time(time1, time2):
    time1 = datetime.datetime.strptime(time1, "%M:%S.%f").time()
    time2 = datetime.datetime.strptime(time2, "%M:%S.%f").time()

    delta = datetime.timedelta(hours=time1.hour, minutes=time1.minute, seconds=time1.second,
                               microseconds=time1.microsecond) + \
            datetime.timedelta(hours=time2.hour, minutes=time2.minute, seconds=time2.second,
                               microseconds=time2.microsecond)

    m, s = divmod(delta.seconds, 60)
    time_formatted = "{:d}:{:02d}.{:03d}".format(m, s, delta.microseconds // 1000)
    print(time_formatted)
    return time_formatted


# 계획 없음 (멘트 섹션 찾기)
def find_contents(radio_name, date):
    pass


###################################### 서비스 로직 ###################################
def get_all_radio_programs():
    with app.app_context():
        # wav 테이블의 pk값을 가져온다.
        # pk는 복합키로 있음
        all_wavs = Wav.query.all()
        all_wavs_json = [{'radio_name': wav.radio_name, 'date': wav.radio_date} for wav in all_wavs]
    return all_wavs_json


###################################### tools ###################################

def get_file_list(file_dir):
    file_list = glob.glob(file_dir + '/*.wav')
    return [os.path.basename(file_path) for file_path in file_list if os.path.isfile(file_path)]


def get_file_path_list(file_dir):
    file_list = []
    os.makedirs(file_dir, exist_ok=True)
    for file_name in os.listdir(file_dir):
        if os.path.isfile(os.path.join(file_dir, file_name)):
            file_list.append(file_dir + "\\" + file_name)
    return file_list


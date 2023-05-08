import os
from models import db, Wav
from app import app
import glob
import time

# for split
import split.split as splitpath
# for stt
import speech_recognition as sr
from google.oauth2 import service_account # 구글 클라우드 인증설정
from google.cloud import storage, speech_v1
from google.oauth2 import service_account
import threading
import datetime
import json

# for audio process
import wave
from pydub import AudioSegment

# logging 미사용 상태임
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

semapore = 0

storage_path = ".\\VisualRadio\\radio_storage"

# ★
def split(song_path, program_name, save_path):
    global semapore
    if semapore == 0:
        semapore += 1
        radio_name = 'brunchcafe'
        date = '230226'
        # 이미 분할 정보가 있는지 확인
        with app.app_context():
            wav = Wav.query.filter_by(radio_name=radio_name, radio_date=date).first()
            if not wav:
                print("해당 라디오 데이터가 없습니다. 먼저 raw.wav를 등록하세요")
                return
            if wav.section != 0: 
                print("분할 정보가 이미 있습니다 - %d 분할" % wav.section)
                return
            else:
                print("분할 로직을 시작합니다")
        
        # 가정: split을 위한 "고정음성"은 fix.db에 등록된 상태다.
        # 주어진 메인 음성을 split한다.

        start_time = time.time()
        splitpath.split(song_path, program_name, save_path)
        end_time = time.time()
        print("분할 처리 시간: ", end_time - start_time, "seconds")

        dir_path = r"D:\JP\Server\VisualRadio\radio_storage\brunchcafe\230226\split_wav"
        wav_files = [f for f in os.listdir(dir_path) if f.endswith('.wav')]

        n = len(wav_files)
        # 분할 완료 후 db 업데이트 - Wav 테이블의 section에 분할개수 insert
        with app.app_context():
            # Wav 모델 인스턴스 생성
            # 복합키를 사용하고 있는 경우, query.get() 메서드를 사용하여 해당 모델 인스턴스를 가져올 수 없습니다. 대신, query.filter() 메서드를 사용하여 복합키를 조건으로 사용하여 쿼리를 실행해야 합니다.
            # wav = Wav.query.get(wav_id)
            wav = Wav.query.filter_by(radio_name=radio_name, radio_date=date).first()
            # section 컬럼에 n 값을 삽입하고 DB에 반영
            if wav:
                wav.section = n
                db.session.commit()
            else:
                pass # 해당 wav 모델 인스턴스가 없을 경우 처리 

        # 분할 결과를 검증한다.
        # 분할 개수를 리턴한다.
        semapore -= 0
        return n
    else: 
        print("오류")
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
def wavToFlac():
    wav_loc = "D:\\JP\\Server\\VisualRadio\\radio_storage\\brunchcafe\\230226\\split_wav"
    flac_loc = "D:\\JP\\Server\\VisualRadio\\radio_storage\\brunchcafe\\230226\\split_flac"
    wav_path = get_file_path_list(wav_loc)
    for order, wav in enumerate(wav_path):
        song = AudioSegment.from_wav(wav)
        song.export(flac_loc + "\\sec_%d.flac" % (order+1), format = "flac")


# ★
def stt(radio_name, date):
    # 모든 section 결과를 무조건 stt한다.
    storage_path = get_storage_path(radio_name, date)
    # section_dir = f'{storage_path}\\split_wav'
    section_dir = f'{storage_path}\\split_flac'
    section_list = os.listdir(section_dir)

    # STT 클라이언트 생성
    project_id = 'RadioProject'
    credentials = service_account.Credentials.from_service_account_file('D:\JP\Server\VisualRadio\credentials.json')
    client = speech_v1.SpeechClient(credentials=credentials)
    # storage_credentials = 
    storage_client = storage.Client(project=project_id, credentials=credentials)

    # 섹션마다 stt 처리하기
    threads = []
    for order, section in enumerate(section_list):
        print("stt할 wav파일 : " + section)
        # STT 수행
        file_path = os.path.join(section_dir, section)

        print("stt대상 파일" + file_path)
        thread = threading.Thread(target=run_quickstart_in_thread, args=(file_path, client, storage_client, order))
        threads.append(thread)
        thread.start()

    # 모든 스레드가 종료될 때까지 대기
    for thread in threads:
        thread.join()

# Define a function to run the quickstart function in a separate thread
def run_quickstart_in_thread(file_path, client, storage_client, order):
    t = threading.Thread(target=run_quickstart, args=(file_path, client, storage_client, order))
    t.start()
    t.join()

def run_quickstart(file_path, client, storage_client, order):
    # 참고: wav가 아닌 flac 기반 stt 진행
    # Speech-to-Text API는 다양한 인코딩을 지원합니다. 아래 표에는 지원되는 오디오 코덱이 나열되어 있습니다.
    # ㄴ> 여기에 wav는 없다
    # https://cloud.google.com/speech-to-text/docs/encoding?hl=ko#compressed_audio

    # Cloud Storage 버킷 이름
    bucket_name = 'radio_bucket'

    # Cloud Storage에 flac 파일 업로드
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(os.path.basename(file_path))

    blob.upload_from_filename(file_path)

    # Cloud Storage에 업로드된 flac 파일 경로
    storage_file_path = f'gs://{bucket_name}/{blob.name}'

    # STT 요청 생성
    audio = speech_v1.RecognitionAudio(uri=storage_file_path)
    config = speech_v1.RecognitionConfig(
        # encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16, 지정하면 google.api_core.exceptions.InvalidArgument: 400 Specify FLAC encoding to match audio file.
        # sample_rate_hertz=get_sample_rate(file_path),
        # WAV 또는 FLAC 파일에 인코딩 및 샘플링 레이트를 지정할 필요가 없습니다. 이를 생략하면 Speech-to-Text가 파일 헤더를 바탕으로 WAV 또는 FLAC 파일의 인코딩과 샘플링 레이트를 자동으로 결정합니다. 파일 헤더의 값과 일치하지 않는 인코딩 또는 샘플링 레이트 값을 지정하면 Speech-to-Text가 오류를 반환합니다.
        # sample_rate_hertz=sf.read(file_path)[1],
        language_code='ko-KR',
        # enable_word_time_offsets=True
        # audio_channel_count = 1
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    # STT 수행
    response = operation.result(timeout=999999)

    # STT 결과 출력
    # for result in response.results:
    #     stt_loc = "D:\\JP\\Server\\VisualRadio\\radio_storage\\brunchcafe\\230226\\raw_stt"
    #     with open(stt_loc + 'stt_%d.txt' % (order + 1), 'a', encoding='UTF8') as f:
    #         f.write(f'Transcript: {result.alternatives[0].transcript}' + '\n')
    #         print(result)

    # stt 결과 가져오기
    results = response.results

    # stt 결과 가져오기 - time format 지정해두기
    start_time_delta = datetime.timedelta(hours=0, minutes=0, seconds=0, microseconds=0)
    m, s = divmod(start_time_delta.seconds, 60)
    start_time_formatted = "{:d}:{:02d}.{:03d}".format(m, s, start_time_delta.microseconds)


    # 이미 json이 있으면 삭제 후 다시 stt 진행
    filename = get_storage_path('brunchcafe', '230226') + '\\raw_stt\\stt_%d.json' % (order+1)
    if os.path.exists(filename):
        os.remove(filename)

    scripts = []
    # stt 결과 가져오기 - text, time에 대한 json 만들기
    for result in results:
        # 각 음성 인식 결과에서 가장 가능성이 높은 대안을 사용
        alternative = result.alternatives[0]  
        new_data = {'time': start_time_formatted, 'txt': alternative.transcript}

        scripts.append(json.dumps(new_data, ensure_ascii=False))

        # start time 갱신
        start_time_delta = result.result_end_time
        m, s = divmod(start_time_delta.seconds, 60)
        start_time_formatted = "{:d}:{:02d}.{:03d}".format(m, s, start_time_delta.microseconds)
        print("stt_%d.json 처리중" % (order+1))
    
    end_time = str(get_flac_duration(file_path))
    data = {'end_time':end_time, 'scripts':[json.loads(s) for s in scripts]}
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f,  ensure_ascii=False)

    print("stt_%d.json 최종 처리 완료" % (order+1))


def get_flac_duration(filepath):
    audio = AudioSegment.from_file(filepath, format="flac")
    duration_micros = int(audio.duration_seconds * 1000000)
    minutes, seconds = divmod(duration_micros / 1000000, 60)
    microseconds = duration_micros % 1000
    return "{:d}:{:02d}.{:03d}".format(int(minutes), int(seconds), microseconds)


# 최종 script.json을 생성한다
def make_txt(radio_name, date):
    print("전체 script.json 생성 시작")
    # stt_n.json 각각을 처리
    # end_time을 고려하여 제작
    storage_path = get_storage_path(radio_name, date)
    stt_dir = f'{storage_path}\\raw_stt'
    stt_list = os.listdir(stt_dir)
    file_path = [os.path.join(stt_dir, name) for name in stt_list]

    script_path = "D:\\JP\\Server\\VisualRadio\\radio_storage\\brunchcafe\\230226\\result\\script.json"
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
            dic_data = {'time':add_time(prev_end_time, text['time']),
                        'txt':text['txt'].strip()}
            new_data.append(dic_data)
        prev_end_time = add_time(prev_end_time, data['end_time'])
    
    
    print("script.json 생성 완료!!!")
    with open(script_path, 'a', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False)


    img_url_1 = "https://img.hankyung.com/photo/202203/01.29353881.1-1200x.jpg"
    img_url_2 = "https://pbs.twimg.com/ext_tw_video_thumb/1514084683608309764/pu/img/1ihM-03RUgNtJqcs.jpg"
    img_url_3 = "https://static.inews24.com/v1/4815fc2c7e522d.jpg"
    img_url_4 = "https://cdn.litt.ly/images/NEpLQ6zpkVRqKo0EzVy3kg1wzlR68XYL?s=1200x630&m=inside"
    
    sec_img_data = []
    img_url_data = [img_url_1, img_url_2, img_url_3, img_url_4]

    with open(file, 'r') as f:
        for idx, time in enumerate(section_start):
            dic_data = {
                'time': time,
                'img_url': img_url_data[idx]
            }
            sec_img_data.append(dic_data)

    with open("D:\\JP\\Server\\VisualRadio\\radio_storage\\brunchcafe\\230226\\result\\section_image.json", 'w', encoding='utf-8') as f:
        json.dump(sec_img_data, f, ensure_ascii=False)
    print("section_image.json 생성 완료!!!")


def add_time(time1, time2):
    time1 = datetime.datetime.strptime(time1, "%M:%S.%f").time()
    time2 = datetime.datetime.strptime(time2, "%M:%S.%f").time()

    delta = datetime.timedelta(hours=time1.hour, minutes=time1.minute, seconds=time1.second, microseconds=time1.microsecond) + \
            datetime.timedelta(hours=time2.hour, minutes=time2.minute, seconds=time2.second, microseconds=time2.microsecond)

    m, s = divmod(delta.seconds, 60)
    time_formatted = "{:d}:{:02d}.{:03d}".format(m, s, delta.microseconds // 1000)
    print(time_formatted)
    return time_formatted


# 계획 없음
def find_contents(radio_name, date):
    storage_path = get_storage_path(radio_name, date)
    stt_list = os.listdir(storage_path + '\\raw_stt')
    stt_list.remove('stt_all.txt')
    # - text 길이를 고려해 target을 찾으면 좋을 듯?
    for stt_name in stt_list:
        file_path = os.path.join(storage_path, '\\raw_stt\\' + stt_name)
        # stt 내용 조회
        with open(file_path, 'r') as f:
            stt_content = f.read()
            # 처리 로직 구현
            #
            #
            # ↓ target일 경우
            target_list.add(stt_name)

    target_list = ['stt_2', 'stt_3']  # 예시 : stt_2, stt_3는 컨텐츠화 가능한 stt결과
    return target_list  


###################################### 서비스 로직 ###################################
def get_all_radio_programs():
    with app.app_context():
        # wav 테이블의 pk값을 가져온다.
        # pk는 복합키로 있음
        all_wavs = Wav.query.all()
        all_wavs_json = [{'radio_name':wav.radio_name, 'date':wav.radio_date} for wav in all_wavs]
    return all_wavs_json



###################################### tools ###################################
def get_storage_path(radio_name, radio_date):
    global storage_path
    return storage_path + '\\' + radio_name + '\\' + radio_date

def get_file_list(file_dir):
    file_list = glob.glob(file_dir + '/*.wav')
    return [os.path.basename(file_path) for file_path in file_list if os.path.isfile(file_path)]

def get_file_path_list(file_dir):
    file_list = []
    for file_name in os.listdir(file_dir):
        if os.path.isfile(os.path.join(file_dir, file_name)):
            file_list.append(file_dir + "\\" + file_name)
    return file_list


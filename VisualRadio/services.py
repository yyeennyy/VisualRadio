# Business Logic Layer(비즈니스 로직 계층)
# 애플리케이션의 비즈니스 로직을 담당하는 계층입니다.
# Presentation Layer에서 전달된 데이터를 처리하고, 필요한 데이터를 데이터 저장 계층에서 조회합니다.


import os
from models import db, Wav
from flask import Flask
from app import app
import glob

# for split
import torchaudio
import torch
import requests
import io
from scipy.io import wavfile
import numpy as np

# 로그 생성 및 설정
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(name)s - %(message)s')
# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(logging.DEBUG)
# stream_handler.setFormatter(formatter)
# logger.addHandler(stream_handler)

storage_path = ".\\VisualRadio\\radio_storage"

###################### db접근 예제 #######################

def service_logic():
    with app.app_context():
        # 컨텍스트 내에서 SQLAlchemy 코드 실행
        wav = Wav.query.filter_by(radio_name='radio1').first()
        print(f"radio name: {wav.radio_name}, radio date: {wav.radio_date}")



########################## 수집기 관련 로직 ##########################

# 저장 로직
def save_wav(wav, radio_url):
    # wav 검증
    # 

    # wav를 radio_url에 저장
    with open(radio_url, 'wb') as f:
        f.write(wav)

    # 처리 결과 리턴
    #


# 로직 1 : raw.wav를 분할한다.
def split(radio_name, date):
    # 이미 분할 정보가 있는지 확인
    with app.app_context():
        wav = Wav.query.filter_by(radio_name=radio_name, radio_date=date).first()
        if not wav:
            print("해당 라디오 데이터가 없습니다. 먼저 raw.wav를 등록하세요")
            return
        if wav.section != 0: 
            print("분할 정보가 이미 있습니다 - %s 분할", wav.section)
            return
        else:
            print("분할 로직을 시작합니다")
    
    radio_url = get_storage_path(radio_name, date)
    print("라디오 스토리지 경로 : " + radio_url)

    fixed_path = f'{radio_url}\\fixed_wav\\'
    url = "http://localhost:5000/radio_storage/%s/%s/split_wav" % (radio_name, date)
    save_url = url

    # fixed_wav 폴더에 있는 고정음성을 이용하여 분할한다.
    # 분할 로직 ##############
    data, sr = torchaudio.load(get_request_url_raw(radio_name, date)) #<=...........................
    print('메인 음성 로딩 완료')
    print(data.shape)

    data_list = data[0].tolist()
    fix_sound_idx = []
    # load fix sound
    fix_file_list = get_file_list(fixed_path)  #<=...................................
    for idx, name in enumerate(fix_file_list):
        print('===============================================')
        tmp, _ = torchaudio.load(get_request_url_fixed(radio_name, date, name))
        tmp = tmp[0].tolist()
        globals()[f'fixed_{idx}'] = tmp
        # print('%d 번째 고정음성 로드 완료 ! 길이는 %d입니다.' % (idx, len(eval('fixed_{}'.format(idx)))))
        print('%d 번째 고정음성 로드 완료 !' % idx)

        
        print('%d 번째 고정음성과 일치하는 부분 탐색 시작' % idx)
        if len(fix_sound_idx)==0:
            start = 0
        else:
            start = fix_sound_idx[-1]+length
        
        for i in range(start, len(data_list)):
            start_point = eval(f'fixed_{idx}')[0]

            if data_list[i] == start_point:
                length = len(eval(f'fixed_{idx}'))
                if eval(f'fixed_{idx}') == data_list[i: i+length]:
                    print('%s 번째 고정음성 찾았음!' % idx)
                    fix_sound_idx.append(i)
                    break
        print('')
    print('분할 지점 탐색 완료 - by 고정음성')    

    return split_by_index(radio_name, date, sr, data_list, fix_sound_idx)


def split_by_index(radio_name, date, sr, data_list, fix_sound_idx):
    print('split 시작')
    saved_list = []
    for i in range(len(fix_sound_idx)-1):
        split = data_list[fix_sound_idx[i]:fix_sound_idx[i+1]]
        split_tensor = torch.Tensor(split)
        split_tensor = split_tensor.reshape(1, -1)

        filepath = os.path.join('D:/JP/Server/VisualRadio/radio_storage/%s/%s/split_wav/' % (radio_name, date), 'sec_%d.wav' % (i+1))
        print(filepath)
        torchaudio.save(filepath, split_tensor, sr)

        saved_list.append("{'저장 경로 :  %s" % (filepath))
        print('%d 번째 파일 저장 완료' % i)

    n = len(saved_list)  # section 개수
    print("=== %d 개로 분할 완료 ===" % n)

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
    return n


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


# 일단 예정 없음
# def find_target():
    # stt 대상을 찾는다 (멘트)
    # 이 라디오 포맷 정보를 참고한다.


import speech_recognition as sr
from pydub import AudioSegment
import wave
import os
import wave
from pydub import AudioSegment
import torch
import torchaudio
import speech_recognition as sr

# TODO: 로직2
# def stt(radio_name, date):
#     # 모든 section 결과를 무조건 stt한다.
#     storage_path = get_storage_path(radio_name, date)
#     section_dir = f'{storage_path}\\split_wav'
#     section_list = os.listdir(section_dir)

#     # TODO: 섹션마다 stt 처리하기
#     for section in section_list:
#         print("stt할 wav파일 : " + section)

#         # stt 로직 ############# 
#         # 'time'다음줄에 'text'가 오도록 결과물 만들기
#         file_path = section_dir + "\\" + section

#         # STT 시작


            
#         # 'time'다음줄에 'text'가 오도록 결과물 만들기



#         print(f'stt완료 (섹션: {section})')
#         #######################
#     # # stt가 완료되어, section마다 stt_1, stt_2, stt_3, ...이 만들어진 상태다.





# TODO: wav to flac (google stt 권장 포맷)
def wavToFlac():
    import services
    wav_loc = "D:\\JP\\Server\\VisualRadio\\radio_storage\\brunchcafe\\230226\\split_wav"
    flac_loc = "D:\\JP\\Server\\VisualRadio\\radio_storage\\brunchcafe\\230226\\split_flac"

    from pydub import AudioSegment
    wav_path = services.get_file_path_list(wav_loc)
    for order, wav in enumerate(wav_path):
        song = AudioSegment.from_wav(wav)
        song.export(flac_loc + "\\sec_%d.flac" % (order+1), format = "flac")


# 구글 클라우드 인증 설정
from google.oauth2 import service_account
from google.cloud import speech_v1
from google.cloud import speech_v1p1beta1 as speech

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
    for order, section in enumerate(section_list):
        print("stt할 wav파일 : " + section)
        # STT 수행
        file_path = os.path.join(section_dir, section)
        print("stt대상 파일" + file_path)
        run_quickstart_in_thread(file_path, client, storage_client, order)



import os
from google.cloud import storage, speech_v1
from google.oauth2 import service_account
import wave

# def get_sample_rate(file_path):
#     sample_rate, _ = wavfile.read(file_path)
#     return sample_rate


import threading

# Define a function to run the quickstart function in a separate thread
def run_quickstart_in_thread(file_path, client, storage_client, order):
    t = threading.Thread(target=run_quickstart, args=(file_path, client, storage_client, order))
    t.start()
    t.join()


def run_quickstart(file_path, client, storage_client, order):

    # Cloud Storage 버킷 이름
    bucket_name = 'radio_bucket'

    # Cloud Storage에 WAV 파일 업로드
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(os.path.basename(file_path))
    # blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024 # ??? timeout문제 때문에 추가함
    # blob._DEFAULT_CHUNKSIZE = 10485760  # 1024 * 1024 B * 10 = 10 MB

    blob.upload_from_filename(file_path)

    # Cloud Storage에 업로드된 WAV 파일 경로
    storage_file_path = f'gs://{bucket_name}/{blob.name}'

    # Speech-to-Text API는 다양한 인코딩을 지원합니다. 아래 표에는 지원되는 오디오 코덱이 나열되어 있습니다.
    # ㄴ> 여기에 wav는 없다
    # https://cloud.google.com/speech-to-text/docs/encoding?hl=ko#compressed_audio

    # STT 요청 생성
    import soundfile as sf
    audio = speech_v1.RecognitionAudio(uri=storage_file_path)
    config = speech_v1.RecognitionConfig(
        # encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16, 지정하면 google.api_core.exceptions.InvalidArgument: 400 Specify FLAC encoding to match audio file.
        # sample_rate_hertz=get_sample_rate(file_path),
        # WAV 또는 FLAC 파일에 인코딩 및 샘플링 레이트를 지정할 필요가 없습니다. 이를 생략하면 Speech-to-Text가 파일 헤더를 바탕으로 WAV 또는 FLAC 파일의 인코딩과 샘플링 레이트를 자동으로 결정합니다. 파일 헤더의 값과 일치하지 않는 인코딩 또는 샘플링 레이트 값을 지정하면 Speech-to-Text가 오류를 반환합니다.
        # sample_rate_hertz=sf.read(file_path)[1],
        language_code='ko-KR',
        enable_word_time_offsets=True
        # audio_channel_count = 1
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=999999)
    # request = speech_v1.RecognizeRequest(audio=audio, config=config)
    # STT 수행
    # response = client.recognize(request=request)

    # STT 결과 출력
    # for result in response.results:
    #     stt_loc = "D:\\JP\\Server\\VisualRadio\\radio_storage\\brunchcafe\\230226\\raw_stt"
    #     with open(stt_loc + 'stt_%d.txt' % (order + 1), 'a', encoding='UTF8') as f:
    #         f.write(f'Transcript: {result.alternatives[0].transcript}' + '\n')
    #         print(result)

    import datetime
    results = response.results
    start_time_delta = datetime.timedelta(hours=0, minutes=0, seconds=0, microseconds=0)
    for result in results:
        # 각 음성 인식 결과에서 가장 가능성이 높은 대안을 사용합니다.
        print("result_start_time: " + str(start_time_delta))
        print("result_end_time: " + str(result.result_end_time))
        start_time_delta = result.result_end_time
        # Time offset of the end of this result relative to the beginning of the audio.
        # A duration in seconds with up to nine fractional digits, ending with 's'. Example: "3.5s".
        
        alternative = result.alternatives[0]
        print(f"Transcription: {alternative.transcript}")
        # for word_info in alternative.words:
            # print(word_info.word)
            # print("단어 start_time: " + word_info.start_time)
            # print("단어 end_time:" + word_info.end_time)
        print("-")



# 로직3
def make_txt(radio_name, date):
    # raw_txt 폴더에 stt결과가 있는지 검증
    # 존재하는 stt_1, stt_2, ... 중에서 컨텐츠화 가능한 것들
    target_list = find_contents(radio_name, date)

    # 컨텐츠화 로직 ###########
    #
    #
    # txt_contents에 저장
    ##########################


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


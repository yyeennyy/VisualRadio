import os
import utils
import json
from models import Process, Wav
import gc
import time
import speech_recognition as sr
import multiprocessing
from torch._C import *
import random
import settings as settings
import librosa
import queue

# logger
from VisualRadio import CreateLogger
logger = CreateLogger("STT")

# STT 도구1 : google
from VisualRadio import db, app
import soundfile as sf

def google_stt(start, audio, sample_rate, interval):
    script = []
    r = sr.Recognizer()

    end = len(audio)
    start_time = 0
    end_time = start_time + interval * sample_rate
    tmp_file = f"temp_{start}.wav"
    while end_time <= end:
        # audio 임시파일 (20초) 
        audio_segment = audio[start_time:end_time]
        sf.write(tmp_file, audio_segment, sample_rate, format="WAV")
        
        # google stt 진행
        try:
            with sr.AudioFile(tmp_file) as tmp:
                tmp_audio = r.record(tmp)
                text = r.recognize_google(tmp_audio, language='ko-KR')
        except sr.RequestError:
            logger.debug(f"[stt] 재시도 {start}")
            sf.write(tmp_file, audio_segment, sample_rate, format="WAV")
            r = sr.Recognizer()
            continue
        except sr.UnknownValueError:
            # 이번 20초는 음성인식 결과가 없을 경우
            text = "(stt결과가 없다.)"
        
        # scipt에 추가
        script.append({f"time":utils.format_time((start_time+start)/sample_rate), "txt":text})

        # 값 갱신
        start_time = end_time
        end_time += interval * sample_rate

    utils.rm(tmp_file)
    return script

from VisualRadio import db, app

def speech_to_text(broadcast, name, date, ment_start_end, audio_holder):
    th_q = queue.Queue()
    logger.debug("[stt] start!")
    start_time = time.time()

    logger.debug(f"[stt] 오디오 로드중..")
    if len(audio_holder.sum) != 0:
        audio_origin = audio_holder.sum
        sr = audio_holder.sr
    else:
        storage = f"{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/"
        audio_origin, sr = librosa.load(os.path.join(storage, "sum.wav"))

    # 작업에 사용할 인자 리스트 준비
    args_list = []
    for order, target in enumerate(ment_start_end):
        start = int(utils.convert_to_second_float(target[0]) * sr)
        end = int(utils.convert_to_second_float(target[1]) * sr)
        args_list.append((broadcast, name, date, start, audio_origin[start:end], sr, order))

    # multiprocessing.Pool을 통한 stt 병렬처리 진행
    with multiprocessing.Pool(processes=8) as pool:
        pool.starmap(stt_proccess, args_list)

    gc.collect()

    end_time = time.time()
    logger.debug(f"[stt] DONE IN {end_time - start_time} SECONDS")

    return


def stt_proccess(broadcast, name, date, start, audio, sr, order):
    # stt 방법 설정
    interval = 20  # seconds
    retries = 0
    MAX_RETRIES = 5
    while retries < MAX_RETRIES:
        try:
            script = google_stt(start, audio, sr, interval)
            break
        except Exception as e:
            logger.error(e)
            logger.debug(f"[stt] {order}번째 stt 다시 시도 중... (남은 시도 횟수: {MAX_RETRIES - retries})")
            retries += 1
            time.sleep(1)  # 잠시 대기 후 다시 시도

    if retries == MAX_RETRIES:
        logger.debug(f"{order} 번째 stt는 다시 해도 안되네요. 처리를 중단합니다.")
        raise Exception("stt 망함")


    # stt조각 저장
    utils.save_json(script, utils.stt_dir(broadcast, name, date, f"{order}.json"))
    logger.debug(f"[stt] 완료! {order}")

    # process테이블 갱신
    with app.app_context():
        process = db.session.query(Process).filter_by(broadcast=broadcast, radio_name=name, radio_date=date).first()
        process.set_end_stt()
        commit(process)

    return

def commit(o):
    db.session.add(o)
    db.session.commit()
    return

def make_script(broadcast, name, date):

    input_dir = utils.checkdir(f"{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/stt/")
    output_dir = f"{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/result/"
    output_filename = "script.json"

    # 딕셔너리 리스트를 저장할 변수 초기화
    combined_list = []

    for i in range(len(os.listdir(input_dir))):
        json_path = os.path.join(input_dir, f"{i}.json")
        
        with open(json_path, "r") as json_file:
            data = json.load(json_file)
            combined_list.extend(data)

    # 결과 리스트를 JSON 파일로 저장하기
    output_path = os.path.join(output_dir, output_filename)
    utils.save_json(combined_list, output_path)
    logger.debug("[stt] script 생성 완료")
    return

def get_stt_target(broadcast, name, date):
    # 저장된 section 정보 가져오기
    with app.app_context():
        wav = Wav.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=str(date)).first()
        radio_section = json.loads(wav.radio_section.replace("'", '"'))

    # 멘트타입(0)인 section 시간대 가져오기
    ment_start_end = []
    for sec in radio_section:
        if sec['type'] == 0:
            ment_start_end.append([sec['start_time'], sec['end_time']])
        # elif sec['type']==1:
            # ment_list.append()

    return ment_start_end
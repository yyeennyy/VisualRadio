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
import whisper
from numba import cuda

# logger
from VisualRadio import CreateLogger
logger = CreateLogger("STT")

# STT 도구1 : google
from VisualRadio import db, app
import soundfile as sf

# regex (종결어미)
import re
endings = ['에요', '해요', '예요', '지요', '네요', '[?]{1}', '[가-힣]{1,2}시다', '[가-힣]{1,2}니다', '어요', '구요', '군요', '어요', '아요', '은요', '이요', '든요', '워요', '드리고요', '되죠', '하죠', '까요', '게요', '시죠', '거야', '잖아']
endings_pattern = '|'.join([re.escape(ending) for ending in endings])
pattern = f"({endings_pattern})"


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




# --------------------- script.json기저장하기 --------------
def get_stt_target(broadcast, name, date):
    # 저장된 section 정보 가져오기
    with app.app_context():
        wav = Wav.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=str(date)).first()
        radio_section = json.loads(wav.radio_section.replace("'", '"'))
    # 멘트타입(0)인 section 시간대 가져오기
    ment_start_end = []
    for sec in radio_section:
        if sec['type'] == 0:
            ment_start_end.append([float(sec['start_time']), float(sec['end_time'])])
    return ment_start_end

def save_ment_script(broadcast, name, date, audio_holder, ment_start_end):
    scripts = audio_holder.jsons 
    results = []
    for txt_info in scripts:
        time = txt_info[0]
        if is_ment(time, ment_start_end):
            results.append(txt_info)
    utils.save_json(results, utils.script_path(broadcast, name, date))
    logger.debug(f"[stt] script.json 저장 완료")  # 기존 후반부에 있던 stt과정이 필요없어진다.


def is_ment(time, ment_start_end):
    for start, end in ment_start_end:
        if start <= time and time < end:
            return True
    return False

# --------------------------------------------------------------------------

# stt작업과 script과정을 분리하지 않은 상태입니다.
# 필요하면 나중에 분리할게요!
def all_stt(audio_holder):
    split_mr = audio_holder.sum_mrs # [[name, audio], ...]

    # ------------------------ stt 작업 ------------------------
    device = utils.device_info()
    # audio를 file로 불러들이는 현시점(whisper timestamp problem)에는 audio array를 cuda에 올리지 않아도 된다.
    # if device == "cuda":
        # audio = torch.tensor(audio, dtype=torch.float32)
        # audio = audio.to(device)

    stt_results = []
    sr = audio_holder.sr
    for data in split_mr:
        name = data[0]
        audio = data[1]
        all_stt_whisper(name, audio, sr, stt_results, device)

    logger.debug(f"[stt] 전체 stt가 생성되었습니다.")
    # ------------------------ stt 작업 완료 --------------------


    # --------------- 전체 script 제작 시작 ------------------
    # whisper stt_results의 text는 "."을 기준 text를 나누어놓았다.
    # 다만, 한단위의 문장보다 잘게 쪼개진 상태다.
    # 문장으로 어느정도 합쳐주어야 스크립트라고 볼 수 있다.
    # 길이 제한을 두자. 적어도 15글자 이상 어때? 할게!
    # -------------------------------------------------------
    # step0) stt["name"]값을 기준으로 natsorted!
    from natsort import natsorted
    stt_sorted = natsorted(stt_results, key=lambda x: x["name"])

    # step1) merge stt data (=> realigning time info)
    # ▼ 각 txt의 time을 재조정(누적)하여 scripts에 추가한다.
    script = []
    cumulative_time = 0
    for stt in stt_sorted: 
        for content in stt["contents"]:
            if content[0] != '':
                time = float(content[0]) + float(cumulative_time)
                txt = content[1]
                script.append({"time":time, "txt":txt})
            else:
                logger.debug(f"[check] {type(content)}")
                logger.debug(f"[check] content[0]가 0인 경우는 뭐지? {content}")
        tmp = []
        tmp.append(stt["name"])
        tmp.append(cumulative_time)
        cumulative_time += stt["duration"]
        tmp.append(cumulative_time)
        audio_holder.durations.append(tmp)
    
    

    # step2) rescripting (=> make a long sentence well..)
    final_script = []
    start_flag = True
    s = ""
    t = ""
    for sentence in script:
        txt = sentence['txt']
        if start_flag:
            t = sentence['time']
            start_flag = False
        s += " " + txt
        if len(s) < 15: # 누적 s가 너무 짧으면 append하지 않는다.
            continue
        else: # 누적 s가 충분히 길면 append한다.
            final_script.append({"time":t, "txt":s.strip()})
            s = ""
            t = ""
            start_flag = True

    audio_holder.jsons = final_script
    audio_holder.jsons.append([{"time":cumulative_time, "txt": ""}])
    logger.debug(f"[stt] 전체 stt를 audio_holder.jsons 등록했습니다.")  # 변수명 jsons 대신에 whole_stt 어때요? 하고싶은대로 하셔요
    logger.debug(f"[stt] {audio_holder.jsons}")
    return audio_holder

import torch
def all_stt_whisper(name, audio, sr, stt_results, device):
    logger.debug(f"[stt] {name}!")
    model = whisper.load_model(settings.WHISPER_MODEL).to(device)
    logger.debug(f"[stt] transcribe")

    # name 경로에 저장된 "mr제거된 wav파일"을 대상으로 stt합니다. whisper의 timestamp 문제 때문에, 기존 array audio를 일단 stt에서 사용하지 않겠습니다.
    # 다른 일이 급하니 경로는 일단 name으로 두겠습니다. (:해당 날짜 디렉토리에 굳이 저장 안하겠다는 의미)
    results = model.transcribe(name, temperature=0.2, word_timestamps=True, condition_on_previous_text=False)
    # 각각의 element: 작은단위의 stt결과가 담김 (i.e. 문장보다 더 잘게 끊긴 text 변환결과)
    s = ""
    t = ""
    prev_string = "" # 이전문자열과 중복 파악을 위함
    sentences = []
    start_flag = True
    stt_data = {}
    for element in results['segments']:
        time = element['start']
        txt = element['text'].strip()
        if prev_string != txt: # 중복되지 않을 경우 문자열을 누적한다.
            s += " " + txt
            prev_string = txt
        else: # 중복될 경우, 다음 txt로 넘어간다.
            if element != results['segments'][-1]:  # 단, 마지막 요소가 아닐 때만 그냥 넘어가고..
                logger.debug(f"중복: {prev_string}")
                continue
        if element == results['segments'][-1]: # 만약 마지막 요소인 경우 누적된 문자열을 append하고 종료한다.
            logger.debug(f"[check] {name} | {t}")
            sentences.append([t, s.strip()])
            break
        if len(txt) == 0:
            continue
        if start_flag:
            t = time
            start_flag = False
        # 정규표현식 패턴에 매치되는지 확인
        # 이 txt에서 끊어야 할 경우다. 누적된 문자열을 append한다.
        if re.search(pattern, txt) or txt[-1]==".":
            logger.debug(f"[check] {name} | {t}")
            sentences.append([t, s.strip()])
            s = ""
            t = ""
            start_flag = True


    stt_data["name"] = name
    stt_data["duration"] = len(audio) / sr
    stt_data["contents"] = sentences

    stt_results.append(stt_data)
    return
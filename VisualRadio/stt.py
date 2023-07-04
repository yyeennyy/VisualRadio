import os
import utils
import json
from models import Process
import gc
import time
import random
import whisper
import wave
from pydub import AudioSegment
import regex as re
from itertools import groupby
import speech_recognition as sr
from pydub import AudioSegment
stt_count = 0
num_file = 0

# logger
from VisualRadio import CreateLogger
logger = CreateLogger("STT")


# TODO: 여기에는 stt만 남기고 나머지 기능(스크립트 만들기..)들은 따로 빼기

from VisualRadio import db, app



def google_stt(src_path, interval, broadcast, name, date):
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
                new_data = {f'time':utils.format_time(start_time / 1000), 'txt':text}
                scripts.append(json.dumps(new_data, ensure_ascii=False))
        except:
            with app.app_context():
                process = Process.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=str(date)).first()
                if process:
                    process.error = 1
                else:
                    process = Process(broadcast=broadcast, radio_name = name, radio_date = date, raw=1, split1=1, split2=1,
                                    end_stt=stt_count, all_stt=num_file, script=0, sum=0, error = 1)
                    db.session.add(process)
                db.session.commit()
                break
        start_time = end_time
        end_time += interval * 1000
    del r
    gc.collect()

    data = {'end_time':utils.format_time(duration), 'scripts':[json.loads(s) for s in scripts]}    
    return data





def whisper_stt(src_path, broadcast, name, date):
    device = "cpu"    #device = "cuda" if torch.cuda.is_available() else "cpu"
    language = "ko"

    while True:
        time.sleep(random.uniform(0.1, 1))
        if utils.memory_usage("stt") > 0.7:
            continue
        # logger.debug(f"[stt] {dst_path}/{save_name} 진행 중")
        try:
            model = whisper.load_model("tiny").to(device)
            results = model.transcribe(
                src_path, language=language, temperature=0.0, word_timestamps=True)
            del model
        except:
             with app.app_context():
                process = Process.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=str(date)).first()
                if process:
                    process.error = 1
                else:
                    process = Process(broadcast=broadcast, radio_name = name, radio_date = date, raw=1, split1=1, split2=1,
                                    end_stt=stt_count, all_stt=num_file, script=0, sum=0, error = 1)
                    db.session.add(process)
                db.session.commit()
                break
        gc.collect()
        logger.debug(utils.memory_usage("stt"))
        break

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
            scripts.append({'time':utils.format_time(times[0]), 'txt':''.join(lines)})
            lines = []
            times = []

    # 결과물의 끝까지 종결 어미가 안나오는 경우이다
    # stt가 잘 안되는 경우, 동일 문장이 반복될 가능성이 높다 (whisper 특성)
    # groupby(lines)를 통해 동일문장을 하나만 반영
    unique_lines = [k for k, _ in groupby(lines)]
    if len(times) != 0:
        scripts.append({'time':utils.format_time(times[0]), 'txt':''.join(unique_lines)})

    # 최종 script를 저장
    with wave.open(src_path, 'rb') as wav_file:
        sample_rate = wav_file.getframerate()
        num_frames = wav_file.getnframes()
        duration = num_frames / sample_rate
    data = {'end_time':utils.format_time(duration), 'scripts':[s for s in scripts]}
    gc.collect()

    return data

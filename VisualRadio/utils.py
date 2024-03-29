import psutil
import shutil
import os
import settings
from datetime import timedelta, datetime

# logger
from __init__ import CreateLogger
logger = CreateLogger("Utils")


def memory_usage(message: str = 'debug'):
    p = psutil.Process()
    rss = p.memory_info().rss # Bytes
    return rss / psutil.virtual_memory().total


from numba import cuda
def device_info():
    if cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
    logger.debug(f"[stt] divice: {device}")
    return device



# ------------------- Path -----------

def get_path(broadcast, name, date):
    return checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/")

def get_rawwavfile_path(broadcast, name, date):
    answer = checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/")
    return os.path.join(answer, "raw.wav")

def hash_splited_path(broadcast, name, date, filepath=""):
    answer = checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/split_wav/{filepath}")
    return answer

def mr_splited_path(broadcast, name, date, filepath=""):
    answer = checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/mr_wav/{filepath}")
    return answer

def tmp_mr_splited_path(broadcast, name, date, filepath=""):
    answer = checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/tmp_mr_wav/{filepath}")
    return answer

def cnn_splited_path(broadcast, name, date, filepath=""):
    answer = checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/split_final/{filepath}")
    return answer

def stt_raw_path(broadcast, name, date, filepath=""):
    answer = checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/raw_stt/{filepath}")
    return answer

def stt_dir(broadcast, name, date, filepath=""):
    answer = checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/stt/{filepath}")
    return answer

def stt_final_path(broadcast, name, date, filepath=""):
    answer = checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/stt_final/{filepath}")
    return answer

def google_script_result_path(broadcast, name, date):
    return checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/{settings.GOOGLE_SAVE_DIR}/")

def whisper_script_result_path(broadcast, name, date):
    return checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/{settings.WHISPER_SAVE_DIR}/")

def script_path(broadcast, name, date):
    return checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/result/script.json")

def section_path(broadcast, name, date):
    return checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/result/section.json")

def sum_wav_path(broadcast, name, date):
    return checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/sum.wav")

def raw_wav_path(broadcast, name, date):
    return checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/raw.wav")


def checkdir(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return path

# .DS_Store 없이!!
def ourlistdir(path):
  return [filename for filename in os.listdir(path) if filename != '.DS_Store']

# (window) 파라미터 디렉토리 하위의 desktop.ini 삭제용
def delete_ini_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".ini"):
                file_path = os.path.join(root, file)
                os.remove(file_path)

# 디렉토리 및 파일 삭제
def rm(path):
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)


def count_files(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        count += len(files)
    return count



# ----------- Time
from datetime import datetime, timedelta


def format_time(time_in_seconds):
    # second 단위 문자열을 "분:초.밀리초" 문자열로 리턴
    time_in_seconds = float(time_in_seconds)
    minutes, seconds = divmod(int(time_in_seconds), 60)
    milliseconds = int((time_in_seconds - int(time_in_seconds)) * 1000)
    return "{:d}:{:02d}.{:03d}".format(minutes, seconds, milliseconds) 


def convert_to_datetime(time_str):
    # "분:초.밀리초" 문자열을 datetime 객체로 반환
    minutes, seconds = time_str.split(':')
    seconds, milliseconds = seconds.split('.')
    
    hours = int(minutes) // 60
    minutes = int(minutes) % 60
    
    time_obj = datetime.min + timedelta(hours=hours, minutes=minutes, seconds=int(seconds), milliseconds=int(milliseconds))
    return time_obj


def convert_to_second_float(time_str):
    # "분:초.밀리초" 문자열을 second단위 float로 변환
    minutes, seconds = time_str.split(':')
    seconds, milliseconds = seconds.split('.')
    
    seconds = int(seconds) + int(minutes) * 60 + float(milliseconds) * 0.001
    
    return seconds


def add_time(time1, time2):
    # "분:초.밀리초" 형식의 시간 문자열 두 개를 더한 시간을 문자열로 리턴
    time1_minutes, time1_seconds_milliseconds = time1.split(":")
    time1_seconds, time1_milliseconds = time1_seconds_milliseconds.split(".")

    time2_minutes, time2_seconds_milliseconds = time2.split(":")
    time2_seconds, time2_milliseconds = time2_seconds_milliseconds.split(".")

    total_minutes = int(time1_minutes) + int(time2_minutes)
    total_seconds = int(time1_seconds) + int(time2_seconds)
    total_milliseconds = int(time1_milliseconds) + int(time2_milliseconds)

    # 초와 밀리초를 조정
    total_seconds += total_milliseconds // 1000
    total_milliseconds %= 1000

    # 분과 초를 조정
    total_minutes += total_seconds // 60
    total_seconds %= 60

    result_time = "{:d}:{:02d}.{:03d}".format(total_minutes, total_seconds, total_milliseconds)
    return result_time


# ----------- Json
import json
def save_json(data, save_dir):
    checkdir(save_dir)
    with open(save_dir, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


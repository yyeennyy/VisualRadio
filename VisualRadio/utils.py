import psutil
import shutil
import os
import settings
from datetime import timedelta, datetime

def memory_usage(message: str = 'debug'):
    # current process RAM usage
    p = psutil.Process()
    rss = p.memory_info().rss # Bytes
    # print(f"[{message}] memory usage: {rss: 10.5f} MB |{type(rss)}| {(rss/5*8*1024)*100}%")
    # logger.debug(rss/(128*1024))
    return rss/psutil.virtual_memory().total




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

def stt_final_path(broadcast, name, date, filepath=""):
    answer = checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/stt_final/{filepath}")
    return answer

def google_script_result_path(broadcast, name, date):
    return checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/{settings.GOOGLE_SAVE_DIR}/")

def whisper_script_result_path(broadcast, name, date):
    return checkdir(f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/{settings.WHISPER_SAVE_DIR}/")

def script_path(broadcast, name, date):
    return f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}/result/script.json"

def checkdir(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return path

# .DS_Store 없이!!
def ourlistdir(path):
  return [filename for filename in os.listdir(path) if filename != '.DS_Store']

# 생성된 결과파일 전부 없애려면 사용 ㄱㄱ
def rmdir(path):
    if os.path.exists(path):
        directory = os.path.dirname(path)
        shutil.rmtree(directory)


# ----------- Time

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


def add_time(time1, time2):
    # "분:시간.초" datetime 객체 두개를 더한 시간을 문자열로 리턴
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


# ----------- Json
import json
def save_json(data, save_dir):
    checkdir(save_dir)
    with open(save_dir, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
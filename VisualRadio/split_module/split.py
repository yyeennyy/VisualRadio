import sys
# sys.path.insert(0, '/app/VisualRadio/split_module')
sys.path.insert(0, './VisualRadio/split_module')
from recognise import find_time
import settings
import sqlite3
import os
from pydub import AudioSegment


def split_about(path, program_name):
    conn = sqlite3.connect('./VisualRadio/split_module/DB/fix.db')
    c = conn.cursor()
    c.execute("SELECT start_time, end_time FROM fix_time WHERE program_name = ?", (program_name,))
    result = c.fetchall()
    conn.close()
    audio = AudioSegment.from_file(path).set_channels(1).set_frame_rate(settings.SAMPLE_RATE)
    real_time = []
    song_info_list = []
    print("result:", result)
    temp_file_path = "./VisualRadio/split_module/tmp.wav"
    for i in range(len(result)):
        start = int(result[i][0])*1000
        end = int(result[i][1])*1000
        if(i == len(result)-1):
            end = min(end, len(audio)-1)
        elif(i == 0):
            start = max(start, 0)
        segment = audio[start:end]
        segment.export(temp_file_path, format='wav')
        song_info, time = find_time(temp_file_path)
        real_time.append(start/1000+time)
        song_info_list.append(song_info)
        os.remove(temp_file_path)  
    
    return song_info_list, real_time


import numpy as np
import librosa
import soundfile as sf
def start_split(path, program_name, save_path, audio_holder):
    song_info, time = split_about(path, program_name)
    # 이제부터 sr을 22050으로 고정적으로 바꿔줍니다. 이는 PR에 자세히 작성하겠습니다.
    audio, sr = librosa.load(path, sr=22050)
    holder_list = []
    for i in range(len(time)):
        start = int(time[i] * sr)
        if i != len(time) - 1:
            end = int(time[i + 1] * sr)
        else:
            end = len(audio) - 1
        seg = audio[start:end]
        seg_path = f"{save_path}/sec_{i}.wav"
        sf.write(seg_path, seg, sr)
        holder_list.append(["sec_" + str(i), seg])

    concatenated_audio = np.concatenate([seg for _, seg in holder_list])
    audio_holder.splits = holder_list
    audio_holder.sum = concatenated_audio
    audio_holder.sr = sr

    return

    
    

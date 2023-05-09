import sys
import sqlite3
import os
from pydub import AudioSegment
import settings as settings
from recognise import find_time

def split_about(path, program_name):
    conn = sqlite3.connect('fix.db')
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

def split(path, program_name, save_path):
    song_info, time = split_about(path, program_name)

    audio = AudioSegment.from_file(path).set_channels(1).set_frame_rate(settings.SAMPLE_RATE)
    for i in range(len(time)):
        start = time[i]*1000
        if(i!=len(time)-1):
            end = time[i+1]*1000
        else:
            end = len(audio)-1
        seg = audio[start:end]
        seg.export(save_path+"/sec_"+str(i)+".wav", format='wav')

    
    

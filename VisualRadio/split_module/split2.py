import os
import pandas as pd
import numpy as np
import librosa
import librosa.display
import tensorflow as tf
import soundfile as sf

# 로거
from VisualRadio import CreateLogger
logger = CreateLogger("우리가1등(^o^)b")

def collect_test(test_path):

    # 음성 데이터 로드
    y, sr = librosa.load(test_path)

    # 음성 데이터를 1초 단위로 자르기
    duration = 1  # 1초
    frame_length = int(sr * duration)
    num_frames = len(y) // frame_length

    x_test = []

    for i in range(num_frames):
        # 음성 데이터에서 현재 프레임을 추출
        frame = y[i * frame_length: (i + 1) * frame_length]

        # 스펙트로그램 생성
        spectrogram = np.abs(librosa.stft(frame))

        x_test.append(np.resize(spectrogram, (128, 128)))

    x_test = np.array(x_test)
    x_test = x_test / 255.0
    
    return x_test

def modify_list(data_list, window_size=20, threshold_0 = 0.9, threshold_1=0.2):
  # 주의!! threshold_1과 threshold_0은 합쳐서 1보다 커야함!
  copy_list = data_list[:]
  for i in range(len(data_list)- window_size+1):
    contain_0 = data_list[i: i+window_size].count(0)
    contain_1 = data_list[i: i+window_size].count(1)
    if(contain_1 > window_size * threshold_1):
      copy_list[i: i+window_size] = [1]*window_size
    if(contain_0 > window_size * threshold_0):
      copy_list[i: i+window_size] = [0]*window_size

  res = copy_list.copy()
  width = int(window_size*(1-threshold_1))
  n = len(copy_list)
  for i in range(n):
      if copy_list[i] == 0:
          start = max(0, i - width)
          end = min(n, i + width + 1)
          res[start:i] = [0] * (i - start)
          res[i:end] = [0] * (end - i)
  return res

def extract_zero_segments(lst):
    zero_segments = []
    start = None
    for i, num in enumerate(lst):
        if num == 0:
            if start is None:
                start = i
        else:
            if start is not None:
                zero_segments.append([start, i-1])
                start = None
    if start is not None:
        zero_segments.append([start, len(lst)])
    return zero_segments

def save_split(test_path, model_path, output_path):
    os.makedirs(output_path, exist_ok=True)
    x_test = collect_test(test_path)
    
    model = tf.keras.models.load_model(model_path)
    
    if x_test.size != 0:
        result = np.squeeze(np.round(model.predict(x_test))).tolist()
        del model
    
    mod_res = modify_list(result)
    ment_range = extract_zero_segments(mod_res)
    
    # 오디오 파일 로드
    audio, sr = librosa.load(test_path, sr=None)

    # 각 구간별로 오디오 자르기
    for idx, segment in enumerate(ment_range):
        start_time, end_time = segment
        start_sample = int(start_time * sr)
        end_sample = int((end_time+1) * sr)
        sliced_audio = audio[start_sample:end_sample]

        # 잘린 오디오 저장
        name = f"/sec_{idx}.wav"
        sf.write(output_path+name, sliced_audio, sr)
        print(f"Segment {idx} 저장 완료: {name}")
    
<<<<<<< HEAD
    return ment_range
=======
    return ment_range
>>>>>>> shin

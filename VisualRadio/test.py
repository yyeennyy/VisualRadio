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

def find_segments(result):
    segments = []
    start_0 = None
    start_1 = None
    count_0 = 0
    count_1 = 0

    for i, val in enumerate(result):
        if val == 0:
            if start_0 is None:
                start_0 = i
            count_0 += 1
        else:
            if count_0 >= 3:
                segments.append((0, start_0, i-1))
            start_0 = None
            count_0 = 0

        if val == 1:
            if start_1 is None:
                start_1 = i
            count_1 += 1
        else:
            if count_1 >= 8:
                segments.append((1, start_1, i-1))
            start_1 = None
            count_1 = 0

    if count_0 >= 3:
        segments.append((0, start_0, len(result)-1))

    if count_1 >= 8:
        segments.append((1, start_1, len(result)-1))

    return segments

def save_split(test_path, model_path, output_path):
    os.makedirs(output_path, exist_ok=True)
    # x_train, y_train = collect_train(train_path)
    x_test = collect_test(test_path)

    model = tf.keras.models.load_model(model_path)
    if x_test.size != 0:
        result = np.round(model.predict(x_test))
        del model
        segments = find_segments(result)
    
    boolean = False
    ment_range = []
    start_t = 0
    end_t = 0

    for segment in segments:
        segment_type, start, end = segment
        if(boolean):
            if(segment_type == 0):
                end_t = end
                continue
            else:
                boolean = False
                ment_range.append([start_t, end_t])
        
        if(segment_type == 0):
            boolean = True
            start_t = start
            end_t = end

    if(boolean):
        ment_range.append([start_t, end_t])

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

    return ment_range
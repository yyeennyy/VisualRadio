import os
import numpy as np
import librosa
from sklearn.preprocessing import MinMaxScaler
from scipy.ndimage import zoom
import torchvision.models as models
import torch
import torch.nn as nn

import soundfile as sf

# 로거
from __init__ import CreateLogger
logger = CreateLogger("우리가1등(^o^)b")

# 모델을 미리 다운 받아놓는 클래스를 정의했습니다.
class SplitMent:
    def __init__(self):
        self.model = None
    
    def set_model(self, model_path): # 인자로 모델 경로를 받은 후,
        model = models.resnet18(pretrained=True)

        # 분류할 클래스의 수
        num_classes = 2 
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, num_classes)

        # 모델을 로드.. cpu 사용합시다 (: cuda 에러 때문에, 임시로)
        model.to("cpu")
        model.load_state_dict(torch.load(model_path))

        self.model = model
        

def find_voice(audio, sr, sec=0.5, threshold=0.009):
  ment_range = []
  window_size = int(sec*sr)
  start = None
  for i in range(0, len(audio), window_size):
    mean = np.mean(np.abs(audio[i: i+window_size]))

    if(mean > threshold):
      if start is None:
        start = i
    else:
      if start is not None:
        ment_range.append([start, i])
        start = None
  if start is not None:
    ment_range.append([start, len(audio)])
  return ment_range

from numba import cuda
import gc


def model_predict(audio, sr, ment_range, split_ment, isPrint=False, sec = 1):
    
    # 이 부분에서, 모델을 로드하지 않고 클래스에서 꺼내오는 방식으로 사용합니다.
    model = split_ment.model
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()  # 모델을 추론 모드로 변경 (필요에 따라 설정)

    real_ment = []
    scaler = MinMaxScaler()
    output_shape = (244, 244)

    for i in ment_range:
        x_test = []
        start = int(i[0])
        end = int(i[1])
        for start in range(start, end, sec*sr):
            end = start+sec * sr
            # 음성 데이터에서 현재 프레임을 추출
            segment = audio[int(start):int(end)]
            
                # 스펙트로그램 생성
            spectrogram = np.abs(librosa.stft(segment))
            normalized_arr = scaler.fit_transform(spectrogram)
            resized_array = zoom(normalized_arr,
                                    (output_shape[0] / normalized_arr.shape[0], output_shape[1] / normalized_arr.shape[1]))

            x_test.append(resized_array)


        # -------- GPU or CPU ---------------
        # if cuda.is_available():
            # x_test를 PyTorch Tensor로 변환
            # x_test = torch.tensor(x_test, dtype=torch.float32)
            # GPU로 이동
            # x_test = x_test.to(device)
            # model = model.to(device)
        # else:
        x_test = np.array(x_test) 
        # ----------------------------------

        # 예측하려는 데이터 (예시: spectrogram_data_resized 변수에 저장된 스펙트로그램 데이터)
        # 이 데이터를 PyTorch 텐서로 변환
        # spectrogram_data = x_test.clone().detach()  # GPU OOM방지
        spectrogram_data = torch.tensor(x_test, dtype=torch.float)
        
        spectrogram_data = spectrogram_data.unsqueeze(1)

        spectrogram_data_resized = torch.cat([spectrogram_data] * 3, dim=1)

        # -------- GPU or CPU ---------------
        # GPU를 사용한다면 텐서를 해당 장치로 이동
        # if cuda.is_available():
            # spectrogram_data = spectrogram_data_resized.to(device)
        # ----------------------------------

        # 예측을 위해 forward pass 실행
        model.eval()
        with torch.no_grad():
            outputs = model(spectrogram_data_resized)

        # 예측된 클래스 레이블을 얻기 위해 클래스 차원(class dimension, axis=1)에서 가장 큰 값의 인덱스를 가져옴
        _, predicted_labels = torch.max(outputs, dim=1)
        
        if(torch.mean(predicted_labels.float()) <= 0.5):
            real_ment.append(i)

    del model
    gc.collect()
    torch.cuda.empty_cache()
    return real_ment

def seconds_to_time_format(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"

def convert_to_time_format(input):
    converted_inner_list = seconds_to_time_format(input)
    return converted_inner_list

def convert_to_time_format_list(input_list):
    result_list = []
    for inner_list in input_list:
        converted_inner_list = [seconds_to_time_format(seconds) for seconds in inner_list]
        result_list.append(converted_inner_list)
    return result_list

def divide_all_elements(input_list, divisor):
    result_list = []
    for inner_list in input_list:
        divided_inner_list = [np.round(element/divisor, 1) for element in inner_list]
        result_list.append(divided_inner_list)
    return result_list

def merge_intervals(intervals, sec_unit):
    merged_intervals = []
    if(len(intervals)==0):
        return merged_intervals
        
    start, end = intervals[0]
    for interval in intervals[1:]:
        if interval[0] - end <= sec_unit:
            end = interval[1]
        else:
            merged_intervals.append([start, end])
            start, end = interval
    merged_intervals.append([start, end])
    return merged_intervals

def drop_doubt_ad(time_range, sec):
    res = []
    for i in time_range:
        if(i[1] - i[0]) >= sec:
            res.append(i)
    return res

def add_length_list(list, length):
    for i in list:
        i[0] += length
        i[1] += length
    return list

def adjust_json_data(json_data, intervals):
    adjusted_data = []
    
    for start, end in intervals:
        start_time = None
        end_time = None
        past_start_time = 0
        for item in json_data:
            json_start_time = item['time']
            
            # 시작시간을 stt가 나눈 시작 시간으로 매핑합니다.
            if start_time is None and past_start_time is not None and past_start_time <= start < json_start_time:
                start_time = past_start_time
                
            # 종료시간을 stt가 나눈 이전 시작 시간으로 매핑합니다.
            if end_time is None and past_start_time is not None and past_start_time < end <= json_start_time:
                end_time = json_start_time
            
            # start와 end가 정해지면 append하고 반복을 종료합니다.
            if start_time is not None and end_time is not None:
                adjusted_data.append([start_time, end_time])
                break
                
            past_start_time = json_start_time
        # 즉, stt구간은 시작시간이므로 마지막 시간이 나와있지 않다. 이러한 부분은 여기서 처리해준다.
        # 멘트라고 판단된 구간이 stt의 제일 마지막 문단 뒤에 하나만 존재할 보장은 없다. 따라서 처음부터 다시 탐색하는 것이 좋다.
        
    return adjust_intervals(adjusted_data) # 마지막으로 구간 다듬기까지!

def adjust_intervals(intervals):
    # 입력된 구간을 시작 시간을 기준으로 정렬
    intervals.sort(key=lambda x: x[0])

    adjusted_intervals = []
    
    if(len(intervals)==0):
        return intervals
    
    current_interval = intervals[0]
    for interval in intervals[1:]:
        if interval[0] <= current_interval[1]:
            # 현재 구간과 다음 구간이 겹칠 경우, 더 큰 범위로 조정
            current_interval[1] = max(current_interval[1], interval[1])
        else:
            # 겹치지 않을 경우, 현재 구간을 결과에 추가하고 다음 구간으로 이동
            adjusted_intervals.append(current_interval)
            current_interval = interval

    # 마지막 구간 추가
    adjusted_intervals.append(current_interval)

    return adjusted_intervals

def extract_not_ment(ment_range, start_time, end_time):
    if len(ment_range) == 0:
        return [[start_time, end_time]]
    
    # 구간 시작점을 기준으로 정렬
    ment_range.sort(key=lambda x: x[0])

    # 결과 리스트 초기화
    result = []

    # 첫 번째 구간의 시작점이 start_time보다 크다면, start_time부터 첫 번째 구간의 시작점까지의 빈 구간 추가
    if ment_range[0][0] > start_time:
        result.append([start_time, ment_range[0][0]])

    # 구간들 사이의 빈 구간을 찾기
    for i in range(1, len(ment_range)):
        prev_end = ment_range[i - 1][1]
        curr_start = ment_range[i][0]
        if curr_start > prev_end:
            result.append([prev_end, curr_start])

    # 마지막 구간의 끝점이 리스트의 길이보다 작다면, 마지막 구간의 끝점부터 리스트의 길이까지의 빈 구간 추가
    last_end = ment_range[-1][1]
    if last_end < end_time:
        result.append([last_end, end_time])

    return result

def merge_and_sort_ranges(range_list1, range_list2):
    merged_ranges = range_list1 + range_list2
    sorted_ranges = sorted(merged_ranges, key=lambda x: x[0])
    return sorted_ranges

def search_legth(audio_holder, name):
    for tmp_list in audio_holder.durations:

        audio_holder_name = tmp_list[0]
        start_time = tmp_list[1]
        end_time = tmp_list[2]

        if audio_holder_name == name:
            return start_time, end_time
        
    

def save_split(audio, name, split_ment, audio_holder): # 섹션마다의 길이를 누적해서 더해줘야함!
    sr = audio_holder.sr
    json_data = audio_holder.jsons
    
    start_time, end_time = search_legth(audio_holder, name)
    
    ment_range = find_voice(audio, sr)
    real_ment = model_predict(audio, sr, ment_range, split_ment)
    real_ment_time = divide_all_elements(real_ment, sr)
    merged_real_ment_time = merge_intervals(real_ment_time, 10)
    ment_without_ad = drop_doubt_ad(merged_real_ment_time, 10) # 20초로 하는게 좋아보임!
    
    # stt로 맞춰야해서 여기 구간조차도 stt에 맞아야함. 즉, 무조건 모든 sec_n 음성이 0부터 시작하면 안됨.
    real_ment_without_ad = add_length_list(ment_without_ad, start_time) 
    
    # 여기에, 우선 ment_without_ad가 들어와야햠.
    adjust_ment = adjust_json_data(json_data, real_ment_without_ad)
    not_ment = extract_not_ment(adjust_ment, start_time, end_time)
    all_range = merge_and_sort_ranges(adjust_ment, not_ment)

    logger.debug(f"real_ment_without_ad : {real_ment_without_ad}")
    logger.debug(f"adjust_ment : {adjust_ment}")
    logger.debug(f"not_ment : {not_ment}")
    
        
    return adjust_ment, all_range, not_ment # content_range
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
from VisualRadio import CreateLogger
logger = CreateLogger("우리가1등(^o^)b")

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


def model_predict(audio, sr, ment_range, model_path, isPrint=False, sec = 1):
    model = models.resnet18(pretrained=True) # 모델의 구조를 정의하고 객체 생성

    # ResNet-18 모델의 fully connected layer를 수정하여 클래스에 맞게 설정
    num_classes = 2  # 분류하려는 클래스 수에 맞게 설정
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)

    model.load_state_dict(torch.load(model_path))
    model.eval()  # 모델을 추론 모드로 변경 (필요에 따라 설정)

    real_ment = []
    scaler = MinMaxScaler()
    output_shape = (244, 244)

    for i in ment_range:
        x_test = []
        start = i[0]
        end = i[1]
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

        x_test = np.array(x_test)

        # 예측하려는 데이터 (예시: spectrogram_data_resized 변수에 저장된 스펙트로그램 데이터)
        # 이 데이터를 PyTorch 텐서로 변환
        spectrogram_data = torch.tensor(x_test, dtype=torch.float)
        
        spectrogram_data = spectrogram_data.unsqueeze(1)

        spectrogram_data_resized = torch.cat([spectrogram_data] * 3, dim=1)

        # GPU를 사용한다면 텐서를 해당 장치로 이동
        spectrogram_data = spectrogram_data_resized.to(device)

        # 예측을 위해 forward pass 실행
        model.eval()
        with torch.no_grad():
            outputs = model(spectrogram_data)

        # 예측된 클래스 레이블을 얻기 위해 클래스 차원(class dimension, axis=1)에서 가장 큰 값의 인덱스를 가져옴
        _, predicted_labels = torch.max(outputs, dim=1)

        # logger.debug(f"{start/sr} {end/sr}")
        # logger.debug(predicted_labels)
        
        if(torch.mean(predicted_labels.float()) <= 0.5):
            real_ment.append(i)
            
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

# 여기에 광고 구간을 쳐내는 로직이 들어가면 딱인데...
def extract_not_ment(ment_range, length):
    if len(ment_range) == 0:
        return [[0, length]]
    
    # 구간 시작점을 기준으로 정렬
    ment_range.sort(key=lambda x: x[0])

    # 결과 리스트 초기화
    result = []

    # 첫 번째 구간의 시작점이 0보다 크다면, 0부터 첫 번째 구간의 시작점까지의 빈 구간 추가
    if ment_range[0][0] > 0:
        result.append([0.0, ment_range[0][0]])

    # 구간들 사이의 빈 구간을 찾기
    for i in range(1, len(ment_range)):
        prev_end = ment_range[i - 1][1]
        curr_start = ment_range[i][0]
        if curr_start > prev_end:
            result.append([prev_end, curr_start])

    # 마지막 구간의 끝점이 리스트의 길이보다 작다면, 마지막 구간의 끝점부터 리스트의 길이까지의 빈 구간 추가
    last_end = ment_range[-1][1]
    if last_end < length:
        result.append([last_end, length])

    return result

def merge_and_sort_ranges(range_list1, range_list2):
    merged_ranges = range_list1 + range_list2
    sorted_ranges = sorted(merged_ranges, key=lambda x: x[0])
    return sorted_ranges

def save_split(model_path, output_path, mr_path): # 섹션마다의 길이를 누적해서 더해줘야함!
    wav_name = output_path.split("/")[-1]
    logger.debug(f"save_split 내에 있는 mr_seg_path는 {mr_path}입니다.")
    os.makedirs(output_path, exist_ok=True)
    
    
    audio, sr = librosa.load(mr_path)
    ment_range = find_voice(audio, sr)
    logger.debug(f"{wav_name} predict 시작")
    real_ment = model_predict(audio, sr,ment_range, model_path)
    real_ment_time = divide_all_elements(real_ment, sr)
    merged_real_ment_time = merge_intervals(real_ment_time, 10)
    ment_without_ad = drop_doubt_ad(merged_real_ment_time, 10) # 20초로 하는게 좋아보임!
    not_ment = extract_not_ment(ment_without_ad, len(audio)/sr)
    all_range = merge_and_sort_ranges(ment_without_ad, not_ment)

    # 여기 광고 구분하는 로직 출현시키기!!!
    
    # 각 구간별로 오디오 자르기
    for idx, segment in enumerate(ment_without_ad):
        start_time, end_time = segment
        start_sample = int(start_time * sr)
        end_sample = int((end_time) * sr)
        sliced_audio = audio[start_sample:end_sample]

        # 잘린 오디오 저장
        name = f"/sec_{idx}.wav"
        sf.write(output_path+name, sliced_audio, sr)
        logger.debug(f"Segment {idx} 저장 완료: {name}")
        
        
    return ment_range, all_range # content_range
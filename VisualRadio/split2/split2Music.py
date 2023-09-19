import numpy as np
import librosa
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import BertModel
from transformers import BertTokenizerFast
import settings as settings

# 로거
from __init__ import CreateLogger
logger = CreateLogger("우리가1등(^o^)b")


class CustomPredictor():
    def __init__(self, model, tokenizer, device):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        
    def predict(self, sentence):
        # 토큰화 처리
        tokens = self.tokenizer(
            sentence,                # 1개 문장 
            return_tensors='pt',     # 텐서로 반환
            truncation=True,         # 잘라내기 적용
            padding='max_length',    # 패딩 적용
            add_special_tokens=True  # 스페셜 토큰 적용
        )
        tokens.to(self.device)
        prediction = self.model(**tokens)
        prediction = F.softmax(prediction, dim=1)
        output = prediction.argmax(dim=1).item()
        return output
    
class CustomBertModel(nn.Module):
    def __init__(self, bert_pretrained, dropout_rate=0.5):
        # 부모클래스 초기화
        super(CustomBertModel, self).__init__()
        # 사전학습 모델 지정
        self.bert = BertModel.from_pretrained(bert_pretrained)
        # dropout 설정
        self.dr = nn.Dropout(p=dropout_rate)
        # 최종 출력층 정의
        self.fc = nn.Linear(768, 2)
    
    def forward(self, input_ids, attention_mask, token_type_ids):
        # 입력을 pre-trained bert model 로 대입
        output = self.bert(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        # 결과의 last_hidden_state 가져옴
        last_hidden_state = output['last_hidden_state']
        # last_hidden_state[:, 0, :]는 [CLS] 토큰을 가져옴
        x = self.dr(last_hidden_state[:, 0, :])
        # FC 을 거쳐 최종 출력
        x = self.fc(x)
        return x
    
def separateNotment(not_ment, json_data):
    res = []
    if(len(not_ment)==0):
        return not_ment
    
    for ran in not_ment:
        start = ran[0]
        end = ran[1]
        
        json_start_time = None
        json_past_start_time = 0
        for item in json_data:
            json_start_time = item['time']
            if start <= json_start_time < end:
                if json_past_start_time is not None and json_start_time is not None:
                    res.append([json_past_start_time, json_start_time])
                
                json_past_start_time = json_start_time
            elif json_start_time == end:
                res.append([json_past_start_time, json_start_time])
            else:
                json_start_time = None
                json_past_start_time = None
    
    if json_past_start_time is not None:
        res.append([json_past_start_time, not_ment[-1][1]])
    return res
    
def split_music_new(json_data, raw_not_ment):
    
    not_ment = separateNotment(raw_not_ment, json_data)
    
    # device = torch.device('cuda:1' if torch.cuda.is_available() else 'cpu')
    device = torch.device('cpu')

    model_path = settings.MUSIC_MODEL_PATH
    CHECKPOINT_NAME = settings.CHECKPOINT_NAME
    bert = CustomBertModel(CHECKPOINT_NAME)
    bert.load_state_dict(torch.load(model_path))
    
    tokenizer = BertTokenizerFast.from_pretrained(CHECKPOINT_NAME)
    
    # CustomPredictor 인스턴스를 생성합니다.
    predictor = CustomPredictor(bert, tokenizer, device)

    music_list = []
    ad_list = []
    for start, end in not_ment:
        logger.debug(f"[{start}, {end}]")
        for item in json_data:
            json_start_time = item['time']
            json_txt = item['txt']
            
            if json_start_time == start:
                output = predictor.predict(json_txt)
                logger.debug(f"json_txt: {json_txt}")
                if output==0:
                    music_list.append([start, end])
                    logger.debug("노래입니다.")
                else:
                    ad_list.append([start, end])
                    logger.debug("광고입니다.")
    return music_list, ad_list

def find_quiet_time(y, sr):
  # 주어진 스펙트로그램 데이터
  y = np.abs(librosa.stft(y))
  spec_data = librosa.amplitude_to_db(y, ref=np.max)
  
  # 소리가 거의 없는 구간을 저장할 리스트
  quiet_segments = []

  # 스펙트로그램에서 어두운 영역을 탐색
  for time_frame, amplitude_frame in enumerate(spec_data.T):
      if np.max(amplitude_frame) <= -60:  # 진폭이 -40 dB 미만인 영역을 소리가 거의 없는 구간으로 간주
          quiet_segments.append(time_frame)

  # 프레임 간격 계산
  hop_length = 512  # STFT에서 사용된 hop length
  frame_interval = hop_length / sr  # 프레임 간격 (초)

  # quiet_segments에 저장된 값으로부터 시간을 계산
  quiet_segments_time = [frame_num * frame_interval for frame_num in quiet_segments]

  lst = []
  for time in quiet_segments_time:
    intTime = int(time)
    contains = False
    for i in lst:
      if(i == intTime):
        contains = True
    if(not contains):
      lst.append(intTime)
      
  if(len(lst)==0):
      return True
  
  merged = []
  sublist = [lst[0]]  # 첫 번째 원소로 시작하는 부분 리스트 생성
  
  for i in range(1, len(lst)):
      diff = lst[i] - lst[i - 1]  # 현재 원소와 이전 원소 사이의 차이 계산
      
      if diff <= 9:
          sublist.append(lst[i])  # 차이가 9 이하이면 부분 리스트에 추가
      else:
          if len(sublist) > 1:
              merged.append(sublist)  # 차이가 9 이상이면 현재 부분 리스트를 합치고 새로운 부분 리스트 생성
          else:
              merged.append([sublist[0]])
          sublist = [lst[i]]
  
  if len(sublist) > 1:
      merged.append(sublist)  # 마지막 부분 리스트를 추가
  else:
      merged.append([sublist[0]])
  
  res = [sublist[0] if len(sublist) == 1 else sublist[0] for sublist in merged]
      
  x = res[0]
  for i in range(1, len(res)):
      y = res[i]
      if(is_difference_valid(x, y)):
          return False
      x = y
  return True

def is_difference_valid(x, y):
    diff = abs(x - y)
    return diff % 20 == 1 or diff % 20 == 19 or diff % 20 == 0

def split_music_origin(y, sr, not_ment):
    music_lst = []
    ad_lst = []
    for ran in not_ment:
        start = ran[0]
        end = ran[1]

        seg = y[int(start*sr):int(end*sr)]

        if(find_quiet_time(seg, sr)):
            music_lst.append(ran)
        else:
            ad_lst.append(ran)
    return music_lst, ad_lst


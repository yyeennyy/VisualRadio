# 전역
from __init__ import db, app
import numpy as np
from models import Contents
import settings as settings

# logger
from __init__ import CreateLogger
logger = CreateLogger("paragraph")

import scipy as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
import konlpy
from konlpy.tag import Okt
from gensim.models import Word2Vec

def distance_of_vectors(v1, v2):
    delta = v1 - v2
    return sp.linalg.norm(delta.toarray())

# 라디오 전용 불용어
stop_words = [
    '아니', '어떻게', '뭐지', '진짜', '정말', '그럼', '근데', '이렇게', '이런', '이게',  
    '어떡해', '뭔데', '뭐냐', '뭐야', '어디', '왜', '어떻게', '이럴수가', '아니라면', '말이야',
    '말인가', '모르겠다', '좀', '조금', '별로', '괜찮다', '아직', '그래', '그럼', '그렇지',
    '이렇게나', '그래서', '일단', '일단', '이제', '이젠', '그러면', '이렇게나', '그러니까', '뭐든',
    '어떤', '어떤', '더', '더', '이', '이', '저', '저', '이', '그래', '그래', '별로', '별로',
    '그렇다', '맞다', '그렇지', '정말', '진짜', '아무리', '게다가', '게다가', '그렇다', '맞다',
    '그렇지', '그런데', '그런데', '별로', '별로', '정말', '진짜', '아무리', '이렇게나', '일단',
    '일단', '이제', '그렇게나', '그렇지', '그러면', '이렇게나', '그러니까', '뭐든', '어떤', '어떤',
    '더', '더', '이', '이', '저', '저', '그리고', '하지만', '그런데', '그래서', '그럼', '또한', '그리하여', '그러나', '이어서', '다만',
    '그렇지만', '그렇게', '그래도', '그럼에도', '그러므로', '그런즉', '이러한', '이와 같이', '따라서',
    '때문에', '한편으로는', '반면에', '비록', '즉시', '이로 인해', '또한', '나아가', '더구나',
    '또한', '더욱이', '게다가', '비롯하여', '더구나', '게다가', '비롯하여', '오직', '다만', '오직',
    '나아가', '이와 같이', '이와 반대로', '이와 달리', '비교적', '비슷하게', '또한', '나아가',
    '이때', '이와 달리', '반면에', '비교적', '비슷하게', '대비하여', '대조적으로', '대조적으로', '비추어보면',
    '비교적', '대비하여', '대조적으로', '비추어보면', '마찬가지로', '아울러', '뿐만 아니라', '예를 들어',
    '또한', '게다가', '오히려', '아직도', '비록', '오히려', '아직도', '비록', '비록', '오히려',
    '전혀', '전혀', '무엇보다도', '아니면', '거꾸로 말하면', '바꿔 말하면', '아니면', '거꾸로 말하면',
    '바꿔 말하면', '더구나', '이와 같이', '게다가', '게다가', '비롯하여', '비교적', '비교적',
    '대비하여', '대비하여', '대조적으로', '대조적으로', '비추어보면', '비추어보면', '전혀', '전혀',
    '무엇보다도', '무엇보다도', '아니면', '아니면', '거꾸로 말하면', '거꾸로 말하면', '바꿔 말하면',
    '바꿔 말하면', '이런 이유로', '이러한 이유로', '이러한 이유로', '따라서', '따라서', '따라서',
    '따라서', '따라서', '만약', '그동안', '제', '못', '몇', '년', '전', '관련', '안', '부', '막', '또', '통해', '님', '주시', '요', '알', '거', '것', '해', '네', '갑자기', '고',
    '보시', '로만'
]
stop_words = list(set(stop_words))


def get_word_set(document):
    word_set = set()
    for sentence in document:
        words_in_document = sentence.split()
        word_set.update(words_in_document)
    return word_set


# ----  document별
import json
import utils
import traceback
import time
import json

def load_script(script_file):
    sentences = []
    sentences_time = []

    # JSON 파일을 읽기 모드로 열기
    with open(script_file, 'r') as json_file:
        ex = json.load(json_file)
        for e in ex:
            sentences.append(e['txt'])
            sentences_time.append(e['time'])

    return sentences, sentences_time

def extract_keywords(sentences, sentences_time, vectorizer, tokenizer):
    tokenizer = Okt()
    target = ['Noun']
    document = []  

    for idx, row in enumerate(sentences):
        line = ''
        words = tokenizer.pos(row)
        for word in words:
            if word[1] in target and word[0] not in stop_words: 
                line += ' ' + word[0]
        if len(line) == 0:
            # logger.debug(f"[형태소 없음] {row}")
            continue
        document.append(line.strip()) 

    vectorized = vectorizer.fit_transform(document)

    num_of_sentences = vectorized.shape[0]
    chunks = []
    chunks_time = []
    chunk = ''
    th = 1.4

    i = 0
    while i < num_of_sentences:
        if len(chunk) == 0:
            chunks_time.append(sentences_time[i])

        now = vectorized.getrow(i)

        if i+1 < num_of_sentences:
            next1 = vectorized.getrow(i+1)
            d1 = distance_of_vectors(now, next1)
        else:
            chunk += " " + sentences[i]
            logger.debug("문단 완성!")
            logger.debug(chunk)
            chunks.append(chunk)
            break
            
        if i+2 < num_of_sentences:
            next2 = vectorized.getrow(i+2)
            d2 = distance_of_vectors(now, next2)
        else:
            chunk += " " + sentences[i] + sentences[i+1]
            logger.debug("문단 완성!")
            logger.debug(chunk)
            chunks.append(chunk)
            break
            
        if d1 < th and d2 > th:
            logger.debug("문장합침1")
            chunk += " " + sentences[i]
            chunk += " " + sentences[i+1]
            i += 2
        elif d2 < th or d1 < th and d2 < th:
            logger.debug("문장합침2")
            chunk += " " + sentences[i]
            chunk += " " + sentences[i+1]
            chunk += " " + sentences[i+2]
            i += 3
        else:
            chunk += " " + sentences[i]
            logger.debug("문단 완성")
            logger.debug(chunk)
            chunks.append(chunk)
            chunk = ''
            i += 1


    return chunks, chunks_time


def extract_tfidf_keywords(chunks, vectorizer):
    tokenizer = Okt()

    target = ['Noun']
    new_chunks = []

    for idx, row in enumerate(chunks):
        line = ''
        words = tokenizer.pos(row)
        for word in words:
            if word[1] in target and word[0] not in stop_words: 
                line += ' ' + word[0]
        if len(line) == 0:
            logger.debug(f"[형태소 없음] {row}")
            line = ''
        new_chunks.append(line.strip()) 

    tfidf_matrix = vectorizer.fit_transform(new_chunks)
    feature_names = vectorizer.get_feature_names_out()
    keywords = []

    for idx, chunk in enumerate(new_chunks):
        keys = []
        tfidf = tfidf_matrix[idx].indices
        for cnt, i in enumerate(tfidf):
            keys.append({"keyword": feature_names[i], "weight": tfidf_matrix[idx, i]})
            if cnt==6: # 키워드의 수를 제한 (가중치 높은 k개만 얻기)
                break
        keys = sorted(keys, key=lambda x: x["weight"], reverse=True)
        keywords.append(keys)

    result = []

    for k in keywords:
        tmp = []
        for k_ in k:
            tmp.append({"keyword": k_["keyword"], "weight": k_["weight"]})
        result.append(tmp)

    return result


def compose_paragraph(script_file):
    
    tokenizer = Okt() # 형태소 분석기 - Okt를 선택 (고유명사를 더 잘 보존)
    vectorizer = TfidfVectorizer(min_df=1, decode_error='ignore') # 벡터화도구
    # model = Word2Vec.load('ko.bin') # 연관어 추출기 - 현재미사용중

    # 작업0: 스크립트 불러오기
    sentences, sentences_time = load_script(script_file)  # TODO: 앵간히 짧은 문장들은 합쳐줘야 결과가 잘 나올텐데..ㅠ
    # 작업3: 문장의 벡터화
    chunks, chunks_time = extract_keywords(sentences, sentences_time, vectorizer, tokenizer)
    # 작업4: 문단 인식 및 키워드 추출
    vectorizer = TfidfVectorizer(min_df=1, decode_error='ignore')
    keywords = extract_tfidf_keywords(chunks, vectorizer)

    logger.debug(f"[compose_paragraph] 만들어진 문단은 {len(chunks)}개 입니다.")
    logger.debug(f"[개수체크] keywords: {len(keywords)}")
    logger.debug(f"[개수체크] chunks_time: {len(chunks_time)}")
    logger.debug(chunks)

    # 결과물
    return chunks, keywords, chunks_time

    



# 임시 검색기능
def tmp_search_paragraph(searchInput):
    result = Contents.query.filter_by(keyword=searchInput).all()
    info = []
    for r in result:
        data = {
            'broadcast':r.broadcast,
            'radio_name':r.radio_name,
            'radio_date':r.radio_date,
            'time':r.time,
            'content':r.content
        }
        info.append(data)
    return info

import os
import sys
import urllib.request
import json


def extract_img(client_id, client_secret, q):
    client_id = client_id
    client_secret = client_secret
    encText = urllib.parse.quote(q)

    url = "https://openapi.naver.com/v1/search/image?query=" + encText # JSON 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        return json.loads(response_body)["items"][0]["link"]
    else:
        logger.debug("Error Code:" + rescode)


def start_extract_image(broadcast, name, date, chunks, chunks_time, keywords):
    logger.debug(f"[extract_img] 이미지 링크 생성중..")
    
    cnt = 0
    with app.app_context():
        try:
            for idx, chunk in enumerate(chunks):
                t = chunks_time[idx]
                keys = keywords[idx]
                logger.debug(f"{keys}에 대한 이미지 링크 추출을 시작합니다.")
                for k in keys:
                    #컨텐츠에 하나하나 등록
                    item = db.session.query(Contents).filter_by(broadcast=broadcast, radio_name=name, radio_date=date, time=t, keyword=k).first()
                    if item == None:
                        if(cnt%10 == 0):
                            time.sleep(1)
                        cnt+=1
                        logger.debug(f"이번 키워드는 {k}입니다.")
                        img_link = extract_img(settings.CLIENT_ID, settings.CLINET_SECRET, k)
                        db.session.add(Contents(broadcast=broadcast, radio_name=name, radio_date=date, time=t, content=chunk, keyword=k, link=img_link))
            db.session.commit()
        except Exception as e:
            logger.debug("[Paragraph] 오류")
            traceback_str = traceback.format_exc()
            logger.debug(traceback_str)

    return


# ---------------- 멘트 컨텐츠를 위한 함수 -------------------------------------------------------------------
import requests
import json
import urllib
from PIL import Image

# 내 api 키
with open('./karlo.txt', 'r', encoding='utf-8') as file:
    key = file.read()
REST_API_KEY = key

# 1: Contents 테이블에서 문단별 time, keyword 가져오기
def get_paragraph_info(broadcast, name, date):
    ########################## 이미지 생성 모드 ####
    ############## mode==1: 키워드 기반           #
    ############## mode==2: 문단 기반             #
    mode = 2
    ##############################################
    with app.app_context():
        result = (
            db.session.query(Contents.time, Contents.keyword, Contents.content)
            .filter(Contents.broadcast == broadcast, Contents.radio_name == name, Contents.radio_date == date)
            .group_by(Contents.time, Contents.keyword)
            .all()
        )

    if mode == 1:
        paragraphs = {}
        for row in result:
            time = row[0]
            prompt = row[1]
            if time not in paragraphs:
                paragraphs[time] = []
                paragraphs[time].append(prompt)
            else:
                paragraphs[time].append(prompt)
    elif mode == 2:
        paragraphs = {}
        for row in result:
            time = row[0]
            prompt = row[2]
            paragraphs[time] = [prompt]

    # 결과 예시: time이 키고 keyword리스트가 값인 딕셔너리
    # paragraphs = {454.33:["가족", "선물", "참여", "퀴즈"], 594.355:["헬스장", "몸", "거울", "방해물"]}
    logger.debug(f"[image] 문단별 키워드를 읽어왔습니다: {paragraphs}")
    return paragraphs


# 번역!
# 한글 -> 영어
def translate_words(paragraphs):
    logger.debug("[image] 키워드를 영번역중.. 좀 오래 걸려요..")
    import googletrans
    translator = googletrans.Translator()
    translator.raise_Exception = True

    # 전체 키워드 수 계산해보기 (쓸모없지만 진행상황 보려고)##############
    total_cnt = 0
    for para_time in paragraphs:
        total_cnt += len(paragraphs[para_time])
    ##################################################################

    done_cnt = 0
    results = []
    memo = {} # 메모이제이션 적용 (번역속도가 아주 느리기 때문)
    for para_time in paragraphs:
        keywords = paragraphs[para_time]
        key_english = []
        for key in keywords:
            if key in memo:
                english = memo[key]
            else:
                english = translator.translate(key, dest='en').text
                memo[key] = english
            key_english.append(english)
            done_cnt += 1
        time.sleep(0.4) # Google Translate HTTP Error 429 too many requests를 피하기 위한 sleep
        results.append({"time":para_time, "keys":", ".join(key_english)})
        logger.debug(f"[image] 번역중.. {round(done_cnt/total_cnt*100, 2)}%")


    logger.debug(f"[image] (드디어) 키워드를 번역했습니다: {results}")
    return results

# 이미지 생성 요청
def t2i(prompt, negative_prompt):
    r = requests.post(
        'https://api.kakaobrain.com/v2/inference/karlo/t2i',
        json = {
            'prompt': prompt,
            'negative_prompt': negative_prompt
        },
        headers = {
            'Authorization': f'KakaoAK {REST_API_KEY}',
            'Content-Type': 'application/json'
        }
    )
    # 응답 JSON
    response = json.loads(r.content)
    return response

def generate_image(broadcast, name, date, english_keywords):
    # ex) input_data: [{'time': 454.33, 'keys': 'family gift Participation Quiz'}, {'time': 594.355, 'keys': 'gym body mirror impediments'}]
        
    done = []
    cnt = 0
    for data in english_keywords:
        time = float(data["time"])
        keys = data["keys"]
        if keys=="" or keys==" ":
            logger.debug(f"[키 없음] {keys}")
            continue
        prompt = data["keys"] + ", illustration style, drawing, painting"
        negative_prompt = "letter, speech bubble, out of frame, signature, text, watermark, duplicate, pattern, cropped, reality, human"

        # 이미지 생성하기 by Kalro
        response = t2i(prompt, negative_prompt)
        cnt += 1
        logger.debug(f"[image] 이미지 생성 완료 {round(cnt/len(english_keywords)*100, 2)}% --- {time}")

        # 응답의 첫 번째 이미지 생성 결과
        if response.get("images") == None:
            continue
        
        result = Image.open(urllib.request.urlopen(response.get("images")[0].get("image")))
        # result.show()
        result.save(utils.checkdir(utils.get_path(broadcast, name, date) + f"para_img/{time}.jpg"))

        # 기존의 radio_section.json 데이터 생성
        content = "ment"
        time_range = f"[{time}:{time+10}]"  # 현상황: 문단 time은 start_time만 있고 end_time은 저장 안하는 상태임. 그런데, script에는 end_time이 없음. 일단 임의로 end_time 넣고 나중에 완성하고 생각하자. 그럼 sub2 로직도 검토해야 할 것임. 
        other = f"/radio_storage/{broadcast}/{name}/{date}/para_img/{time}.jpg"  # 이 경로는 이미지요청 라우트함수로, 새로 구현해야 한다. | 라우트함수의 리턴 이미지: /radio_storage/broadcast/name/date/time.jpg
        done.append({"content":content, "time_range":time_range, "other":other})
    
    file_path = utils.get_path(broadcast, name, date) + "result/section.json"
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = [] # 파일이 없을 경우 빈 리스트로 초기화
 
    data.extend(done)

    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False)

    logger.debug(f"[image] section.json 저장 완료!")
    
    return

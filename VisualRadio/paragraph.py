# 전역
from VisualRadio import db, app
import numpy as np
from models import Contents
import settings as settings

# logger
from VisualRadio import CreateLogger
logger = CreateLogger("paragraph")

# 벡터화 도구
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(min_df=1, decode_error='ignore')
from scipy.sparse import csr_matrix
import scipy as sp
def distance_of_vectors(v1, v2):
    delta = v1 - v2
    return sp.linalg.norm(delta.toarray())

# 형태소 분석기 - Okt를 선택 (고유명사를 더 잘 보존)
import konlpy
from konlpy.tag import Okt
tokenizer = Okt()

# 연관어 추출기
from gensim.models import Word2Vec
model = Word2Vec.load('VisualRadio/ko.bin')

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

def compose_paragraph(broadcast, name, date):
# 작업0: 스크립트 불러오기
    # 스크립트 
    sentences = []
    sentences_time = []
    # JSON 파일을 읽기 모드로 열기
    with open(utils.script_path(broadcast, name, date), 'r') as json_file:
        ex = json.load(json_file)
        for e in ex:
            sentences.append(e['txt'])
            sentences_time.append(e['time'])

    # 작업1: 원하는 형태소만 남긴다 (처리를 위해)
    target = ['Noun']
    document = []  
    indexs = []       
    for idx, row in enumerate(sentences):
        line = ''
        words = tokenizer.pos(row)
        for word in words:
            if word[1] in target and word[0] not in stop_words: 
                line += ' ' + word[0]
        if len(line) == 0:
            # print(f"[형태소 없음] {row}")
            continue
        document.append(line.strip()) 
        indexs.append(idx)

    # 작업2: 연관 단어를 추가! (등장했다고 가정하는 셈)
    # word_set = get_word_set(document)
    # new_document = []
    # for sentence in document:
    #     new_sentence = []
    #     for w in sentence.split(" "):
    #         new_sentence.append(w)
    #         try:
    #             sim = model.wv.most_similar(w)
    #             new_sentence.extend([element[0] for element in sim if element[1] > 0.7 and element[0] in word_set and element[0] != word][:2])
    #         except:
    #             pass
    #     new_document.append(" ".join(new_sentence).strip())

    # document = new_document
    # print(document)

    # 작업3: 문장의 벡터화
    vectorized = vectorizer.fit_transform(document)
    # print("sentenses & tokens :", vectorized.shape[0], "&", vectorized.shape[1])

    # 작업3-1: 벡터값 조정
    # new_vectorized = []
    # for v in vectorized.toarray():
    #     top_indices = np.argsort(v)[-9:]
    #     result_vector = np.zeros_like(v)
    #     # 상위 값은 그대로, 나머지는 0으로 설정
    #     result_vector[top_indices] = v[top_indices]
    #     new_vectorized.append(result_vector)
    # print("벡터값 k개 미만으로 조정 완료 (연관된 문장인데도 단어수가 차이나서 distance가 증가되는 것을 방지 | 또는 연관 안된 문장인데도 단어수가 많아서 착각하는 것 방지)")
    # vectorized = csr_matrix(new_vectorized)

    # 작업4: 문단 인식 시작
    num_of_sentences = vectorized.shape[0]
    visit = [False] * len(sentences)
    chunks = []
    chunks_time = []
    chunk = ''

    # vectorized를 기반으로 유사한 문장끼리 문단 묶기 시작!
    i = 0
    th = 1.4
    while i < num_of_sentences:
        if len(chunk) == 0:
            chunks_time.append(sentences_time[indexs[i]])
        if not visit[indexs[i]]:
            chunk += " ▶ " + sentences[indexs[i]]
            # print(sentences[indexs[i]])

        now = vectorized.getrow(i)

        if i+1 < num_of_sentences:
            next1 = vectorized.getrow(i+1)
            d1 = distance_of_vectors(now, next1)
        if i+2 < num_of_sentences:
            next2 = vectorized.getrow(i+2)
            d2 = distance_of_vectors(now, next2)
        if i+3 < num_of_sentences:
            next3 = vectorized.getrow(i+3)
            d3 = distance_of_vectors(now, next3)

        if i+3 < num_of_sentences:
            if d1 < th and d3 > th-0.1:
                chunk += " ▶ " + sentences[indexs[i+1]]
                visit[indexs[i+1]] = True
                i += 1
            elif d2 < th and d3 > th-0.1:
                chunk += " ▶ " + sentences[indexs[i+1]]
                chunk += " ▶ " + sentences[indexs[i+2]]
                visit[indexs[i+1]] = True
                visit[indexs[i+2]] = True
                i += 2
            else:
                if d3 <= th-0.1:
                    chunk += " ▶ " + sentences[indexs[i+1]]
                    chunk += " ▶ " + sentences[indexs[i+2]]
                    chunk += " ▶ " + sentences[indexs[i+3]]
                    visit[indexs[i+1]] = True
                    visit[indexs[i+2]] = True
                    visit[indexs[i+3]] = True
                    i += 3
                    continue
                chunks.append(chunk)
                chunk = ''
                i += 1
        else:
            chunks.append(chunk)
            chunks.append(" ▶ ".join(sentences[-3:]))
            chunks_time.append(sentences_time[indexs[i]])
            chunk = ''
            break

    # 최종 chunks에서 키워드추출
    target = ['Noun']
    new_chunks = []
    indexs = []       
    for idx, row in enumerate(chunks):
        line = ''
        words = tokenizer.pos(row)
        for word in words:
            if word[1] in target and word[0] not in stop_words: 
                line += ' ' + word[0]
        if len(line) == 0:
            print(f"[형태소 없음] {row}")
            continue
        new_chunks.append(line.strip()) 
        indexs.append(idx)
    tfidf_matrix = vectorizer.fit_transform(new_chunks)
    feature_names = vectorizer.get_feature_names_out() # 단어목록 추출
    keywords = []
    for idx, chunk in enumerate(new_chunks):
        keys = []
        tfidf = tfidf_matrix[idx].indices
        for i in tfidf:
            keys.append([feature_names[i], tfidf_matrix[idx, i]])
            
        keys = sorted(keys, key=lambda x: x[1], reverse=True)
        keywords.append(keys)
    result = []
    for k in keywords:
        tmp = []
        for k_ in k:
            tmp.append(k_[0])
        result.append(tmp)
    keywords = result

    # 결과물
    logger.debug(f"[compose_paragraph] 만들어진 문단은 {len(chunks)}개 입니다.")
    logger.debug(f"[extract_img] 이미지 링크 생성중..")
    with app.app_context():
        try:
            for idx, chunk in enumerate(chunks):
                t = chunks_time[idx]
                keys = keywords[idx]
                for k in keys:
                    #컨텐츠에 하나하나 등록
                    item = db.session.query(Contents).filter_by(broadcast=broadcast, radio_name=name, radio_date=date, time=t, keyword=k).first()
                    if item == None:
                        img_link = extract_img(settings.CLIENT_ID, settings.CLINET_SECRET, k)
                        db.session.add(Contents(broadcast=broadcast, radio_name=name, radio_date=date, time=t, content=chunk, keyword=k, link=img_link))
            db.session.commit()
        except Exception as e:
            logger.debug("[Paragraph] 오류")
            traceback_str = traceback.format_exc()
            logger.debug(traceback_str)


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
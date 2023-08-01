import wave
import os
from natsort import natsorted
import json
import utils
from sqlalchemy.exc import IntegrityError
from VisualRadio import db, app
from models import Listener, Process, Keyword
import settings
import re
from konlpy.tag import Komoran
from sklearn.feature_extraction.text import TfidfVectorizer


# logger
from VisualRadio import CreateLogger
logger = CreateLogger("script")



def before_script(broadcast, name, date, start_times, stt_tool_name):
    raw_stt = utils.stt_raw_path(broadcast, name, date)
    sec_n = utils.ourlistdir(raw_stt)
    duration_dict = get_duration_dict(broadcast, name, date)
    # sec_n
    for key in sec_n:
        stt_segment_path = utils.stt_raw_path(broadcast, name, date, f'{key}/{stt_tool_name}')
        segments = natsorted(utils.ourlistdir(stt_segment_path))
        time_start = start_times[f'{key}.wav']
        new_lines_sec_n = []
        for idx, segment in enumerate(segments): # 각각의 sec_i.json에 대해서..
            # print(segment) # sec_i.json
            with open(f'{stt_segment_path}/{segment}', 'r', encoding='utf-8') as f:
                data = json.loads(f.read())
            lines = data["scripts"]
            for line in lines:
                # 시간정보 업데이트
                new_lines_sec_n.append({'time':utils.add_time(time_start[idx], line['time']), 'txt':line['txt']})
        
        # 최종 sec_n.json 생성 시작
        result_sec_n = {}

        result_sec_n['end_time'] = utils.format_time(duration_dict[key])
        result_sec_n['scripts'] = new_lines_sec_n

        filename = f'{key}.json'
        # 파일 생성
        save_path = utils.stt_final_path(broadcast, name, date, f"{stt_tool_name}/{filename}")
        utils.rmdir(save_path)
        with open(f'{save_path}', 'w') as f:
            f.write(json.dumps(result_sec_n, ensure_ascii=False))


# 최종 script.json을 생성한다.
# google과 whisper의 stt 결과를 모두 고려한다.
def make_script(broadcast, name, date):
    logger.debug("[make_script] script.json 생성중")

    # google
    stt_dir = utils.stt_final_path(broadcast, name, date, "google/")
    stt_list = natsorted(utils.ourlistdir(stt_dir))
    targets = [os.path.join(stt_dir, name) for name in stt_list]
    save_path = utils.google_script_result_path(broadcast, name, date) + "script.json"
    if os.path.exists(save_path):
        os.remove(save_path)
    with open(save_path, 'w') as f:
        f.write('')
    make_script_2(targets, save_path)

    # whisper
    stt_dir = utils.stt_final_path(broadcast, name, date, "whisper/")
    stt_list = natsorted(utils.ourlistdir(stt_dir))
    targets = [os.path.join(stt_dir, name) for name in stt_list]
    save_path = utils.whisper_script_result_path(broadcast, name, date) + "script.json"
    if os.path.exists(save_path):
        os.remove(save_path)
    with open(save_path, 'w') as f:
        f.write('')
    section_start = make_script_2(targets, save_path)
    
    # 각 section의 stt결과를 합쳐 찐막 scripts를 만든다.
    correct_applicant(broadcast, name, date)
    logger.debug("[make_script] 사연자 보정 완료 => 최종 script.json 생성")
    
    global stt_count, num_file
    # DB - script를 True로 갱신
    with app.app_context():
        process = Process.query.filter_by(broadcast=broadcast, radio_name=name, radio_date=str(date)).first()
        if process:
            process.script = 1
            db.session.add(process)
            db.session.commit()
        else:
            logger.debug(f"[make_script] [오류] {name} {date} 가 있어야 하는데, DB에서 찾지 못함")
    generate_images_by_section(broadcast, name, date, section_start)

# file_path에 있는 sections를 처리하여 save_path에 script.json을 저장한다.
def make_script_2(file_path, save_path):
    new_data = []
    section_start = []
    prev_end_time = "0:00.000"
    for file in file_path:
        section_start.append(prev_end_time)
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        scripts = data['scripts']
        for text in scripts:
            dic_data = {'time': utils.add_time(prev_end_time, text['time']),
                        'txt': text['txt'].strip()}
            new_data.append(dic_data)
        prev_end_time = utils.add_time(prev_end_time, data['end_time'])
    with open(save_path, 'a', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False)
    return section_start

import math
from datetime import datetime, timedelta
time_format = '%M:%S.%f'
number_dir = {'일': 1, '이': 2, '삼': 3, '사': 4, '오': 5, '호':5, '육': 6, '유': 6, '칠': 7, '팔': 8, '구': 9, '국':9, '군':9, '영': 0, '공':0, '하나': 1, '둘': 2, '셋': 3, '넷': 4, '다섯': 5, '여섯': 6, '일곱': 7, '여덟': 8, '아홉': 9}
def correct_applicant(broadcast, name, date):
    path = f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}"
    g_path = f"{path}/{settings.GOOGLE_SAVE_PATH}"
    w_path = f"{path}/{settings.WHISPER_SAVE_PATH}"
    save_path = f"{path}/{settings.SAVE_PATH}"

    # step1)
    # whisper 결과를 기준으로 google 결과를 매치
    # 텍스트 비교해보기
    with open(w_path, 'r', encoding='utf-8') as w:
        wdata = json.load(w)
    with open(g_path, 'r', encoding='utf-8') as g:
        gdata = json.load(g)

    g_text_prev = ""
    g_applicant = {}
    w_applicant = {}
    g_concat = []
    for w in wdata:
        w_time = w['time']
        w_dtime = utils.convert_to_datetime(w_time)
        w_text = w['txt']
        for g in gdata:
            g_time = g['time'][:-4] + '.000'
            g_dtime = utils.convert_to_datetime(g_time)
            g_text = g['txt']
            if w_dtime >= g_dtime: 
                g_concat.append(g_text)
            else:
                ' '.join(g_concat)
                g_concat = []
                break
        if g_text != g_text_prev:
            # print("\n┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────")
            # print("●", g_time, "[google]", g_text)
            if applicant_number(g_text) != None:
                # print("            사연자 : ", applicant_number(g_text))
                g_applicant[g_time] = applicant_number(g_text)
            # print("└───────────────────────────────────────────────────────────────────────────────────────────────────────────────")
            
        g_text_prev = g_text
        # print(w_time, ">>", w_text)
        if applicant_number(w_text) != None:
            # print("            사연자 : ", applicant_number(w_text))
            w_applicant[w_time] = applicant_number(w_text)

    # 이제부터 만들 결과물 : [멘트시간, 잘못된번호, 올바른번호]
    should_choice = {}
    this_is_true = {}
    tmp = set()
    for w_key in w_applicant:
        w_time = utils.convert_to_datetime(w_key)
        w_element = w_applicant.get(w_key)
        for g_key in g_applicant:
            g_element = g_applicant.get(g_key)
            g_time = utils.convert_to_datetime(g_key)
            # 기존: 겹치는 것만 고려했음
            if abs(w_time - g_time) <= timedelta(seconds=10):
                if w_element[1] != g_element[1]:
                    should_choice[w_key] = [w_element[1], g_element[1]]
                else:
                    this_is_true[w_key] = [w_element[0], w_element[1]]
                tmp.add(g_key)
        # 수정: whisper 단독도 true로 처리
        if w_key not in this_is_true:
            this_is_true[w_key] = [w_element[0], w_element[1]]

    for t in tmp:
        g_applicant.pop(t)

    google_alone = g_applicant
    logger.debug(f"[correct_applicant] 다음은 애매하여 처리하지 않았음 {should_choice}")
    logger.debug(f"[correct_applicant] 확실한 수정사항: {this_is_true}")
    # should_choice : 애매한 청취자 정보
    # this_is_true : 확실한 보정 정보
    # google_alone : 구글에만 탐지된 청취자 정보

    # google만 인식한 것은 whisper에서 어떨까?
    # +=10 범위에 숫자 인식 비슷하게 한 거 있으면, 그걸 후보군에 넣자.
    target_text = []   
    for g_key in google_alone:
        # print(g_key, google_alone.get(g_key))
        g_time = utils.convert_to_datetime(g_key)
        for w in wdata:
            w_key = w['time']
            w_time = utils.convert_to_datetime(w_key)
            if abs(g_time - w_time) < timedelta(seconds=10):
                # print(w_key, w['txt']) # target임
                target_text.append([w_key, w['txt'], google_alone.get(g_key)])
                # print('--------------')

    applicants_added_back = {}
    for text in target_text:
        w_key = text[0]
        w_text = text[1]
        g_hints = text[2]
        cnt = 0
        # logger.debug("--------- 청취자 찾는중 ----------")
        for hint in g_hints:
            contained = find_similar_strings(hint, w_text)
            if contained != None:
                cnt += 1
                # logger.debug(contained, "at", w_text)
            if cnt == len(g_hints):
                # logger.debug("---------- 최종 반영 ---------")
                # logger.debug(f"{w_key}에 {g_hints[1]} 청취자 정보 찾음")
                added = f"{w_text} :: ※ {g_hints[1]}청취자"
                logger.debug(added)
                applicants_added_back[w_key] = added
        # if target_text[-1] == text:
            # logger.debug("--------- 청취자 찾기 끝 ---------")
    logger.debug(f"added back: {applicants_added_back}")


    # 찾은 결과를 실제로 반영한다.
    # applicants_added_back : 정확히 대체하지 못함. 청취자번호를 뒤에 그냥 추가할 것임
    # this_is_true : 확실한 사연자 보정 정보
    result_data = []
    for w in wdata:
        if w['time'] in applicants_added_back:
            logger.debug(f"┌변환 전: {w['txt']}")
            w['txt'] = applicants_added_back.get(w['time']).strip()
            logger.debug(f"└변환 후: {w['txt']}")
        for w_key in this_is_true:
            if w['time'] == w_key:
                a = this_is_true.get(w_key)[0]
                b = this_is_true.get(w_key)[1]
                logger.debug(f"┌변환 전: {w['txt']}")
                w['txt'] = w['txt'].replace(a, b+"님")
                logger.debug(f"└변환 후: {w['txt']}")
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(wdata, f, ensure_ascii=False)
    logger.debug("[correct_applicant] 사연자 보정 완료")


# 만들어진 스크립트에서 청취자 찾아 키워드 추출

def get_token(komoran, sentence):
    pos_tags = komoran.pos(sentence)
    keywords = [word[0] for word in pos_tags if word[1]=='NNG' or word[1]=='NNP'] # 일반명사, 고유명사
    if len(keywords) == 0:
        return ''
    return keywords[0]

def register_listener(broadcast, name, date):
    script_file = utils.script_path(broadcast, name, date)
    if not os.path.exists(script_file):
        logger.debug(f"[find_listner] 경고: 만들어진 script가 없어서 중단한다 {broadcast} {name} {date}")
        return False
    with open(script_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    scripts = {}
    for line in data:
        scripts[line['time']] = line['txt']

    # data 반복문
    # - scripts에 target_txt 반영 (원본 스크립트가 아니라, tf-idf에 넣을 스크립트)
    # - 청취자 감지 내용을 listeners에 담기
    listeners = []
    regex = "(?<![0-9])(?<![0-9] )[0-9]{4}(?!년| 년)(?! [0-9])(?![0-9])"
    flag = 0
    tmp_idx = -1
    already = False
    target_txt = ""
    # 가정: 청취자 코드 등장 이후, 연속 몇 문장은 하나의 내용이다.
    for idx, line in enumerate(data):
        txt = line['txt']
        time = line['time']
        person_list = re.findall(regex, txt)
        if (already and len(person_list)!=0) or flag == 5: # 5개 문장 반영
            if len(person_list)!=0:
                # 일단 반영하고.. 
                already = True
                scripts[time_pin] = target_txt
                target_txt = scripts[time_pin]
                listeners.append({'time':time_pin, 'code':code_pin, 'txt':target_txt, 'txt_index':tmp_idx})
                # 청취자 등장 시점과 동일한 처리
                tmp_idx += 1
                idx_pin = idx
                time_pin = time
                code_pin = person_list[0]
                target_txt = data[idx_pin]['txt']
                flag = 1
                continue
            else:
                already = False
                scripts[time_pin] = target_txt + data[idx]['txt']
                target_txt = scripts[time_pin]
                flag = 0
                scripts.pop(time)
                listeners.append({'time':time_pin, 'code':code_pin, 'txt':target_txt, 'txt_index':tmp_idx})
                continue
        # 문장 누적 시점
        if already:
            target_txt += " " + data[idx]['txt']
            flag +=1
            scripts.pop(time)
            continue
        tmp_idx += 1
        if len(person_list) == 0: # 청취자 부분 아니면 스킵
            continue
        else: # 청취자 등장 시점
            already = True
            idx_pin = idx
            time_pin = time
            code_pin = person_list[0]
            target_txt = data[idx_pin]['txt']
            flag = 1
            continue

    # script 반복문
    # tf-idf 키워드를 추출하는 부분
    # 실제 적용시 listeners의 내용을 DB에 추가하면 된다. (code & keywords & time & target_txt)
    komoran = Komoran()
    vectorizer = TfidfVectorizer()
    doc = [value for time, value in scripts.items()]
    tfidf_matrix = vectorizer.fit_transform(doc) # tf-idf 가중치 계산
    feature_names = vectorizer.get_feature_names_out() # 단어목록 추출
    pick = 5 # 선청할 키워드 수 maximum
    for info in listeners:
        time = info['time']
        txt = info['txt']
        txt_index = info['txt_index']
        # txt에 대해서 keywords 추출 시작!
        keywords = []
        tmp_keys = {}
        for j, idx in enumerate(tfidf_matrix[txt_index].indices):
            token = get_token(komoran, feature_names[idx])
            if len(token) == 0:
                # token = feature_names[idx]
                continue
            if len(token)>1 and tmp_keys.get(token) == None:
                keywords.append([token, tfidf_matrix[txt_index, idx]])
                tmp_keys[token] = 1
        keywords = sorted(keywords, key=lambda x: x[1], reverse=True)
        info['keywords'] = keywords[:pick]
        info.pop('txt_index')

    # DB에 저장(Keyword테이블, Listener테이블)
    for l in listeners:
        print(l['txt'])
        print(l['code'], ": ", l['keywords'])
        print()
        with app.app_context():
            try:
                db.session.add(Listener(broadcast=broadcast, radio_name=name, radio_date=date, code=l['code'], preview_text=l['txt'], time=l['time']))
                stop_words = ['제가']
                result = [keyword[0] for keyword in l['keywords'] if l['keywords'][0] not in stop_words]
                result =  ' '.join(str(item) for item in result[:3])
                keyword = Keyword(broadcast=broadcast, radio_name=name, radio_date=date, code=l['code'], keyword= result, time=l['time'])
                db.session.add(keyword)
                db.session.commit()
            except IntegrityError as e:
                logger.debug("IntegrityError occurred............")
    logger.debug(f"[find_listner] 청취자 등록 완료") 


###################################### tools ###################################



def applicant_number(text):
    if "문자" in text and ("샵" in text or "#" in text):
        return
    # 가능한 정규표현식이 최대한 매치되어야 하는 것이 관건
    number_re1 = r"(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1})(|,| |\.)?(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1}(?!에)(|,| |\.)?){2,3}(?![0-9])(?!씩|원))( )?[군|범|번]{1}( )?[님|림]{1})"
    number_re2 = r"(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1})(|,| |\.)?(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1}(?!에)(|,| |\.)?){2,3}(?![0-9])(?!씩|원))( )?[군|범|번]?( )?[님|림]{1})"
    number_re3 = r"(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1})(|,| |\.)?(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1}(?!에)(|,| |\.)?){2,3}(?![0-9])(?!씩|원))( )?[군|범|번]{1}( )?[님|림]?)"
    number_re4 = r"(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1})(|,| |\.)?(((일|이(?!런)(?! 하나 둘)|삼|사|오|육|칠|팔|구|국|공|영|하나(?! 둘이)(?!둘이)|둘|호|유|[0-9]){1}(?!에)(|,| |\.)?){2,3}(?![0-9])(?!씩|원))( )?[군|범|번]?( )?[님|림]?)"
    reg_list = [number_re1, number_re2, number_re3, number_re4]
    for reg in reg_list:
        pattern = re.compile(reg)
        match = pattern.search(text)
        if match:
            raw = match.group().strip()
            if re.match(r'^\d{4}$', raw):
                return None
            fix = ''.join(str(number_dir.get(c, c)) for c in raw).replace(",","").replace(" ", "")
            fix = re.findall(r'\d{4}', fix)
            fix = ''.join(fix)
            if len(raw.replace(" ", "").replace(",", "")) >= 4:
                return [raw, fix]
            else:
                return None
    return None

# 사연자 찾기 도구들
def get_g_key_1(time_str):
    minutes, seconds = time_str.split(':')
    seconds = math.floor(float(seconds))
    time_str = f'{minutes}:{str(seconds).zfill(2)}.000'
    return time_str
def get_g_key_2(time_str):
    minutes, seconds = time_str.split(':')
    seconds = math.ceil(float(seconds))
    if seconds == 60:
        minutes = str(int(minutes) + 1)
        seconds = 0
    time_str = f'{minutes}:{str(seconds).zfill(2)}.000'
    return time_str
def get_ngrams(string, n):
    ngrams = []
    for i in range(len(string) - n + 1):
        ngram = string[i:i+n].strip()
        ngrams.append(ngram)
    return ngrams
def find_similar_strings(target, string):
    target_ngrams = get_ngrams(target, len(target)//2)
    contained = []
    finded = False
    for ngram in target_ngrams:
        if string.find(ngram) != -1:
            contained.append(ngram)
            finded = True
    if finded:
        return contained
    return None



def get_duration_dict(broadcast, name, date):
    wav_path = utils.hash_splited_path(broadcast, name, date)
    stt_path = utils.stt_raw_path(broadcast, name, date)
    sorted = natsorted(utils.ourlistdir(wav_path))
    stts = natsorted(utils.ourlistdir(stt_path))

    duration_dict = {}
    all_duration = {}
    for key in sorted:
        key = key[:-4]
        wav_file = f'{wav_path}/{key}.wav'
        with wave.open(wav_file, 'rb') as f:
            sample_rate = f.getframerate() 
            num_frames = f.getnframes()  
            duration = num_frames / sample_rate
        all_duration[key] = duration

    # 기준 : stts
    # 이동 : sorted
    p = 0
    for idx, target in enumerate(stts):
        duration_dict[target] = 0
        while True:
            if sorted[p][:-4] != target:
                duration_dict[stts[idx-1]] += all_duration[sorted[p][:-4]]
                # print(stts[idx-1], "에 ", sorted[p][:-4], "저장")
                p += 1
                continue
            duration_dict[target] = all_duration[target]
            # print(sorted[p], target)
            p += 1
            break

    return duration_dict


# ------------------- ImageGenerator

import random
def generate_images_by_section(broadcast, name, date, section_start_list):
    path = f"./{settings.STORAGE_PATH}/{broadcast}/{name}/{date}"
    
    sec_img_data = []
    for idx, time in enumerate(section_start_list):
        dic_data = {
            'time': time,
            'img_url': f"https://picsum.photos/300/300/?image={random.randrange(0,100)}"
        }
        sec_img_data.append(dic_data)

    with open(f"{path}/{settings.IMAGE_PATH}", 'w', encoding='utf-8') as f:
        json.dump(sec_img_data, f, ensure_ascii=False)
    logger.debug("[make_script] section_image.json 생성 완료!!!")
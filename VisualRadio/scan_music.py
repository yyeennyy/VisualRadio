import json
import re
import utils

# 로거
from __init__ import CreateLogger
logger = CreateLogger("music")


# music sentences 파악을 위한 고정값
def register_song_pattern(arr, pattern, front_cut, back_cut):
    map = {}
    map['pattern'] = pattern
    map['front_cut'] = front_cut #('의', '<')
    map['back_cut'] = back_cut   #('들려', '<')
    arr.append(map)
p1 = r"[0-9가-힣a-z ]+의\s*[0-9가-힣a-z ]+\s*듣고 오"
p2 = r"[0-9가-힣a-z ]+의\s*[0-9가-힣a-z -]+\s*들려드립"
p3 = r"[0-9가-힣a-z ]+신청하신\s*[0-9가-힣a-z ]+\s*듣고 오"
p4 = r"[0-9가-힣a-z ]+님이[0-9가-힣a-z ]+신청하신\s*[0-9가-힣a-z -]+\s*"
p5 = r"신청곡[0-9가-힣a-z ]+들려\s*[0-9가-힣a-z -]+"
p6 = r"신청곡[0-9가-힣a-z ]+듣고\s*[0-9가-힣a-z -]+"
p7 = r"신청곡[0-9가-힣a-z ]+듣겠\s*[0-9가-힣a-z -]+"
p8 = r"[0-9가-힣a-z ]+의[0-9가-힣a-z ]+신청\s*[0-9가-힣a-z -]+"
regex_list = [p1, p2, p3, p4, p5, p6, p7, p8]
split_word = ['이어서요']
# music을 찾기 위한 regex를 '패턴'으로 등록
arr = []
register_song_pattern(arr, p1, ('의', '<'), ('듣고', '<'))
register_song_pattern(arr, p2, ('의', '<'), ('들려', '<'))
register_song_pattern(arr, p3, ('신청하신', '>'), ('듣고', '<'))
register_song_pattern(arr, p4, ('신청하신', '>'), ('', ''))
register_song_pattern(arr, p5, ('신청곡', '>'), ('들려', '<'))
register_song_pattern(arr, p6, ('신청곡', '>'), ('듣고', '<'))
register_song_pattern(arr, p7, ('신청곡', '>'), ('듣겠', '<'))
register_song_pattern(arr, p8, ('의', '<'), ('신청', '<'))


def find_music_sentences(broadcast, name, date):
    with open(utils.script_path(broadcast, name, date), 'r', encoding='utf-8') as file:
        data = json.load(file)

    ok = False
    sentences = []
    for info in data:
        time = info['time']
        txt = info['txt']
        for element in arr:
            pattern = element['pattern']
            front_cut = element['front_cut']
            back_cut = element['back_cut']
            matches = re.findall(pattern, txt)
            for match in matches:
                for s in split_word:
                    if s in txt:
                        splited = txt.split(s)
                        sentences.append({'txt':splited[0].strip(), 'time':time, 'front_cut':front_cut, 'back_cut':(s, '<')})
                        sentences.append({'txt':splited[1].strip(), 'time':time, 'front_cut':(s, '>'), 'back_cut':back_cut})
                    else:
                        sentences.append({'txt':match, 'time':time, 'front_cut':front_cut, 'back_cut':back_cut})
                ok = True
                break
            if ok is True:
                ok = False
                break

    for s in sentences:
        logger.debug(s)
    return sentences


def get_music_search_word(sentences):
    logger.debug("------------------ 문장 정리하여 검색어 얻기 ---------------------------")
    search_words = []
    for sentence in sentences:
        txt = sentence['txt']
        f_word = sentence['front_cut'][0]
        f_space = sentence['front_cut'][1]
        b_word = sentence['back_cut'][0]
        b_space = sentence['back_cut'][1]

        f_index = txt.find(f_word)
        if f_index != -1:
            if f_space == '<':
                txt = txt[:] # 일단 잘 되니까 반례찾기 전까지는 그냥.. 
            elif f_space == '>':
                txt = txt[f_index+len(f_word):]

        b_index = txt.rfind(b_word)
        if b_index != -1:
            if b_space == '<':
                txt = txt[:b_index]
            elif b_space == '>':
                txt = txt[b_index+len(b_word):]

        search_words.append({'txt':txt.strip(), 'time':time, 'front_cut':front_cut, 'back_cut':back_cut})

    for s in search_words:
        logger.debug(s['txt'])

    return search_words


def get_retry_music_target(search_words):
    logger.debug("\n---------------------다시 고려할 것:")
    one_more_time = []
    for s in search_words:
        if len(s['txt']) >= 20:
            logger.debug(s['txt'])
            one_more_time.append(s)
            search_words.remove(s)
    return one_more_time


def retry_find_music_sentences(one_more_time):
    logger.debug("\n--------------------한번 더 적용")
    sentences = []
    for info in one_more_time:
        time = info['time']
        txt = info['txt']
        for element in arr:
            pattern = element['pattern']
            front_cut = element['front_cut']
            back_cut = element['back_cut']
            matches = re.findall(pattern, txt)
            for match in matches:
                for s in split_word:
                    if s in txt:
                        splited = txt.split(s)
                        sentences.append({'txt':splited[0].strip(), 'time':time, 'front_cut':front_cut, 'back_cut':(s, '<')})
                        sentences.append({'txt':splited[1].strip(), 'time':time, 'front_cut':(s, '>'), 'back_cut':back_cut})
                    else:
                        sentences.append({'txt':match, 'time':time, 'front_cut':front_cut, 'back_cut':back_cut})
                ok = True
                break
            if ok is True:
                ok = False
                break
    return sentences


def get_youtube_search_words(broadcast, name, date):
    youtube_search_words = []
    sentences = find_music_sentences(broadcast, name, date)
    search_words = get_music_search_word(sentences)
    youtube_search_words.append(search_words)
    one_more_time = get_retry_music_target(search_words)
    sentences = retry_find_music_sentences(one_more_time)
    search_words = get_music_search_word(sentences)
    youtube_search_words.append(search_words)
    logger.debug("[scan_music] 유튜브 노래 검색어 추출 완료")
    logger.debug(f"[scan_music] {youtube_search_words}")
    # return format: [{"time":~~(초형식)~~, "txt":~~~~}, ...]
    return youtube_search_words
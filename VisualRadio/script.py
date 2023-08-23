import wave
import os
from natsort import natsorted
import json
import utils
from VisualRadio import db, app
from models import Process


# logger
from VisualRadio import CreateLogger
logger = CreateLogger("script")

def stt(broadcast, name, date, start_times):
    logger.debug(start_times)

    raw_stt = utils.stt_raw_path(broadcast, name, date)
    sec_n = utils.ourlistdir(raw_stt)
    duration_dict = wav_duration_dict(broadcast, name, date)

    # sec_n
    for key in sec_n:
        bigger_stt_path = utils.stt_raw_path(broadcast, name, date, f'{key}')
        smaller_stt_list = natsorted(utils.ourlistdir(bigger_stt_path))
        time_start = start_times[f'{key}.wav']
        all_sentences = []
        for idx, small_stt in enumerate(smaller_stt_list): # 각각의 sec_i.json에 대해서..
            with open(f'{bigger_stt_path}/{small_stt}', 'r', encoding='utf-8') as f:
                data = json.loads(f.read())
            lines = data["scripts"]
            for line in lines:
                # 시간정보 업데이트
                all_sentences.append({'time':utils.add_time(utils.format_time(time_start[idx]), line['time']), 'txt':line['txt']})
        
        # 최종 sec_n.json 생성 시작
        sec_n_concated = {}
        sec_n_concated['end_time'] = duration_dict[key]
        sec_n_concated['scripts'] = all_sentences

        filename = f'{key}.json'
        # 파일 생성
        save_path = utils.stt_final_path(broadcast, name, date, f"{filename}")
        with open(f'{save_path}', 'w') as f:
            f.write(json.dumps(sec_n_concated, ensure_ascii=False))


# 최종 script.json을 생성한다.
def make_script(broadcast, name, date):
    logger.debug("[make_script] script.json 생성중")

    # 경로 설정
    stt_dir = utils.stt_final_path(broadcast, name, date)
    stt_list = natsorted(utils.ourlistdir(stt_dir))
    targets = [os.path.join(stt_dir, name) for name in stt_list]
    save_path = utils.script_path(broadcast, name, date) + "script.json"
    if os.path.exists(save_path):
        os.remove(save_path)
    with open(save_path, 'w') as f:
        f.write('')

    # 스크립트 생성
    final_script = []
    # section_start = []
    prev_end_time = "0:00.000"
    for file in targets:
        # section_start.append(prev_end_time)
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        scripts = data['scripts']
        for text in scripts:
            dic_data = {'time': utils.add_time(prev_end_time, text['time']),
                        'txt': text['txt'].strip()}
            final_script.append(dic_data)
        prev_end_time = utils.add_time(prev_end_time, data['end_time'])
    with open(save_path, 'a', encoding='utf-8') as f:
        json.dump(final_script, f, ensure_ascii=False)
    # return section_start
    logger.debug("[make_script] 최종 script.json 생성")

    # DB에 진행사항 기록
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



def wav_duration_dict(broadcast, name, date):
    wav_path = utils.hash_splited_path(broadcast, name, date)
    stt_path = utils.stt_raw_path(broadcast, name, date)
    waves = natsorted(utils.ourlistdir(wav_path))
    stts = natsorted(utils.ourlistdir(stt_path))

    duration_dict = {}
    all_duration = {}
    for key in waves:
        key = key[:-4]
        wav_file = f'{wav_path}/{key}.wav'
        with wave.open(wav_file, 'rb') as f:
            sample_rate = f.getframerate() 
            num_frames = f.getnframes()  
            duration = num_frames / sample_rate
        all_duration[key] = duration

    # wav조각에 대해 stt결과가 있을 수도, 없을 수도 있다. 
    # stt 문장 출현시간정보를 기록해야 하므로, wav조각의 duration을 고려하여 각 stt파일의 시작시간을 기록해야 한다.
    # 그래서 stt 결과가 없는 wav건에 대하여, 이전 stt의 duratoin을 늘려서 다음 stt가 그 duration만큼 늦게 시작되도록 반영하였다. 
    p = 0
    for idx, target in enumerate(stts):
        duration_dict[target] = 0
        while True:
            if waves[p][:-4] != target:
                duration_dict[stts[idx-1]] += all_duration[waves[p][:-4]]
                p += 1
                continue
            duration_dict[target] = all_duration[target]
            p += 1
            break
    
    # 최종 완결된 각stt의 duration 포맷을 통일시켜 저장한다.
    for element in duration_dict:
        duration_dict[element] = utils.format_time(str(int(duration_dict[element])))
    return duration_dict



# ■삭제1)
# 기존 청취자 보정 기능 : '일이삼사'를 1234로 보정해야 했음.
# 다만 google의 경우 스크립트에서 청취자 번호 보정이 일단 필요가 없다.
# 그래서 아예 기능을 삭제했다. 
# 나중에 whisper를 재도입할 때에도, 새로 구현하는 것이 깔끔할 것 같다. 일단 현재 커밋에는 사용하지 않는 기능은 아예 삭제했다.

# ■삭제2)
# Listener 테이블을 구축하는 부분을 삭제하였다.
# 만들어진 스크립트에서 청취자를 찾아 사연문단을 구성하고, 사연의 키워드를 뽑는 부분이다.
# 삭제한 이유는: 다시 필요할 때 재구현하거나 그때 기능추가하는 것이 깔끔할 것 같아서이다.
# 즉: 지금은 삭제해두고 재등장시키겠다.
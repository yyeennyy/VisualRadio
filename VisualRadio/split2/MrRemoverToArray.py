from spleeter.separator import Separator
import time
import numpy as np
from joblib import Parallel, delayed
from VisualRadio import CreateLogger
import threading
import gc


class MrRemoverToArray:
    def __init__(self):
        self.is_running = False
        self.is_done = False
        self.thread = None
        self.separator = Separator('spleeter:2stems')
        self.split_mrs = []
        self.name_list = []
        self.wav = None
    
    def set_name(self, name):
        self.name = name
        self.name_list.append(name)

    def start(self):
        self.is_running = True
        self.is_done = False
        self.start_time = time.time()  # 작업 시작시간 기록
        self.thread = threading.Thread(target=self.background_process)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=0.1)

    def background_process(self):
        while self.is_running:
            y = self.separator.separate(self.wav) # 오래 걸리는 작업
            vocal = y['vocals']
            mono_data = np.mean(vocal, axis=1)
            self.split_mrs.append([self.name, mono_data])
            self.is_running = False
            self.is_done = True
            
            
def cutting_audio(duration, audio_holder):

    # 작업에 사용할 인자 리스트 준비
    splits = audio_holder.splits
    for split in splits:
        split_name = split[0]
        audio = split[1]
        logger.debug(f"{split_name}의 audio.shape는 {audio.shape}입니다.")
        sr = audio_holder.sr

        idx = 0
        logger.debug(f"[mr제거] {int(duration/60)}분 파일로 쪼개 저장중: {split_name}")
        seg = False
        if(len(audio) > duration*sr):
            seg = True
            for i in range(0, len(audio)-duration*sr, duration*sr):
                seg_audio = audio[i : i+duration*sr]
                save_name = f"{split_name}-{str(idx)}.wav"
                audio_holder.tmps.append([save_name, seg_audio])
                logger.debug(f"[cutting audio] {save_name}의 seg_audio.shape : {seg_audio.shape}")
                idx+= 1
        save_name = f"{split_name}-{str(idx)}.wav"
        
        if not seg:
            audio_holder.tmps.append([save_name, audio])
            logger.debug(f"[cutting audio] save_name : {save_name}")
            logger.debug(f"[cutting audio] seg_audio : {audio}")
            logger.debug(f"[cutting audio] seg_audio.shape : {audio.shape}")
        else:
            seg_audio = audio[i+duration*sr:len(audio)]
            audio_holder.tmps.append([save_name, seg_audio])
            logger.debug(f"[cutting audio] save_name : {save_name}")
            logger.debug(f"[cutting audio] seg_audio : {seg_audio}")
            logger.debug(f"[cutting audio] seg_audio.shape : {seg_audio.shape}")
        
       
        
        
    return

logger = CreateLogger("services")


def remove_mr_to_array(audio_holder, duration=int(600/2)):
    logger.debug("[mr제거] 시작")

    # 오디오 커팅
    cutting_audio(duration, audio_holder)

    #--------------------------------------------------------------
    # MR제거
    
    seg_list = audio_holder.tmps

    mr_remover = MrRemoverToArray()
    for seg_mr in seg_list:
        logger.debug(f"[mr제거] {seg_mr[0]} mr 제거중..")

        mr_remover.set_name(seg_mr[0])
        wav_reshape = np.reshape(seg_mr[1], (-1, 1))
        mr_remover.wav = wav_reshape
        mr_remover.start()
        try:
            while True:
                time.sleep(10)
                gc.collect()
                # 작업이 너무 오래 걸릴 경우 재시작 & 초기화
                # 설정해둔 시간값: duration / 2 : 쪼갠파일이 맥시멈 10분이면, 5분안에 처리되도록 의도
                if mr_remover.is_running and not mr_remover.is_done:
                    elapsed_time = time.time() - mr_remover.start_time
                    if elapsed_time > int(duration/3): 
                        logger.debug(f"[mr제거] {seg_mr[0]} 오래 걸려서 재시작")
                        mr_remover.stop()
                        mr_remover = None
                        mr_remover = MrRemoverToArray()
                        mr_remover.set_name(seg_mr[0])
                        mr_remover.start()
                        gc.collect()
                elif not mr_remover.is_running and mr_remover.is_done:
                    break
        except:
            print("에러")

    mr_remover.stop()
    
    
    #--------------------------------------------------------------

    section_wav__names = mr_remover.split_mrs
    name_list = []

    logger.debug("여기부터 시작")
    for fname, wav in section_wav__names:
        rname = fname.split("-")[0]
        if rname+".wav" in name_list:
            continue
        logger.debug(f"[mr제거] 오디오 합치는 중.. {fname}")
        x = wav
        for name, other_wav in section_wav__names:
            if(fname == name):
                continue
            r2name = name.split("-")[0]
            if(r2name == rname):
                logger.debug(f"{fname}과 {name}이 같습니다.")
                logger.debug(f"other_wav.shape : {other_wav.shape}")
                x = np.concatenate((x, other_wav), axis=0)
        direct = f"{rname}.wav"
        logger.debug(f"[mr제거] {direct}의 길이는 {x.shape}이고 sr은 {audio_holder.sr}입니다.")
        audio_holder.sum_mrs.append([direct, x])
        name_list.append(direct)
    
    # print(audio_holder.sum_mrs)
    logger.debug("끝, 이 전에 긴 문장이 나와야해여")
    logger.debug(f"audio_holder.sum_mrs : {audio_holder.sum_mrs}")
    # print(mr_remover.name_list)
    # audio_holder.sr = int(audio_holder.sr/2)
    mr_remover = None
    gc.collect()
    return
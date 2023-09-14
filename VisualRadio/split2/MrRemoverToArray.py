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
        self.input_mrs = []
    
    def start(self):
        # update status
        self.is_running = True
        self.is_done = False
        self.start_time = time.time()
        # start theadings
        self.thread = threading.Thread(target=self.background_process)
        self.thread.start()

    def stop(self):
        self.is_running = False
        self.separator = None
        if self.thread:
            self.thread.join(timeout=0.1)

    def background_process(self):
        while self.is_running:
            # input_mrs
            for target in self.input_mrs:
                name = target[0]
                audio = target[1]
                logger.debug(f"[mr제거] {name}.. 오디오 길이 {len(audio)}")
                y = self.separator.separate(audio) # 오래 걸리는 작업
                vocal = y['vocals'] 
                logger.debug(f"[mr제거] {name}.. 추출된 vocals 길이 {len(vocal)}")
                mono_data = np.mean(vocal, axis=1)
                logger.debug(f"[mr제거] {name}.. 만들어진 mono_data 길이 {len(mono_data)}")
                self.split_mrs.append([name, mono_data])
                logger.debug(f"[mr제거] 완료되었습니다. spleeter객체를 초기화해볼게요!") # mr제거 결과가 하나씩 밀리는 문제를 객체초기화로 해결!
                self.separator = Separator('spleeter:2stems')
            self.is_running = False
            self.is_done = True
            return
            
            
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

    # MR 제거--------------------------------------------------------------
    # bring seg from audio holder
    seg_list = audio_holder.tmps
    mr_remover = MrRemoverToArray()

    # target reshape
    mr_targets = []
    for seg_mr in seg_list:
        seg_name = seg_mr[0]
        wav_reshape = np.reshape(seg_mr[1], (-1, 1))
        mr_targets.append([seg_name, wav_reshape])

    # removing process in MrRemover!
    mr_remover.input_mrs = mr_targets
    mr_remover.start()

    # 기존의 try-except 구문은 간소화해두겠습니다.
    # 필요성 불필요성은 차선으로 두겠습니다.
    try:
        while True:
            time.sleep(5) # 5초마다 종료 체크
            if not mr_remover.is_running and mr_remover.is_done:
                break
    except:
        print("에러")
    mr_remover.stop()
    #--------------------------------------------------------------
    
    section_wav__names = mr_remover.split_mrs
    name_list = []

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
        # 임시 변경 : whisper의 timestamp문제를 해결하고자, 기존 array audio가 아닌 wav로 whisper의 오디오파일 파라미터로 넣겠습니다.
        import soundfile as sf
        sf.write(direct, x, audio_holder.sr)
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
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
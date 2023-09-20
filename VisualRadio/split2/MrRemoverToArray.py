from spleeter.separator import Separator
import time
import numpy as np
from joblib import Parallel, delayed
from __init__ import CreateLogger
import threading
import gc


class MrRemoverToArray:
    def __init__(self):
        self.split_mrs = []
        self.input_mrs = []


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

    # remove mr! -------------------------------------------------
    mr_remover.input_mrs = mr_targets
    for target in mr_remover.input_mrs:
        name = target[0]
        audio = target[1]
        logger.debug(f"[mr제거] {name}.. 오디오 길이 {len(audio)}")
        try:
            separator = Separator('spleeter:2stems')
            y = separator.separate(audio) # 오래 걸리는 작업
        except:
            logger.debug("[mr제거] 오류 pass")
        vocal = y['vocals']
        mono_data = np.mean(vocal, axis=1)
        mr_remover.split_mrs.append([name, mono_data])
    del separator
    gc.collect()
    #--------------------------------------------------------------
    
    section_wav__names = mr_remover.split_mrs
    name_list = []

    for fname, wav in section_wav__names:
        rname = fname.split("-")[0]
        if rname+".wav" in name_list:
            continue
        logger.debug(f"[mr제거] 오디오 합치는 중.. {rname}으로..")
        x = wav
        for name, other_wav in section_wav__names:
            if(fname == name):
                continue
            r2name = name.split("-")[0]
            if(r2name == rname):
                x = np.concatenate((x, other_wav), axis=0)
        direct = f"{rname}.wav"

        audio_holder.sum_mrs.append([direct, x])
        name_list.append(direct)
    
    mr_remover = None
    gc.collect()
    return
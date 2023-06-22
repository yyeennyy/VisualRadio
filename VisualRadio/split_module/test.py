from register import *
from fingerprint import *
import settings
from DB.setup_db import setup_db
from DB.fix_db import setup_fix_db
from recognise import *
from split import *

# # # # 1. db를 생성한다.
# setup_db()
# setup_fix_db()

# # # # # 2. 고정음성의 대략적인 시간대를 입력한다.
# # # # # store_time(라디오 프로그램 이름, 고정음성 이름, 시작시간(s), 종료시간(s), 순서)
# 이석훈
# store_time("brunchcafe", "start", "6", "15")
# store_time("brunchcafe", "part1_start", "660", "720")
# store_time("brunchcafe", "mbc", "1715", "1740")
# store_time("brunchcafe", "part2_start", "1770", "1835")
# store_time("brunchcafe", "finish", "3360", "3480")

# 윤도현
# store_time("4시엔윤도현입니다", "1", "10", "16")
# store_time("4시엔윤도현입니다", "2", "1715", "1723")
# store_time("4시엔윤도현입니다", "3", "1800", "1810")
# store_time("4시엔윤도현입니다", "4", "3425", "3435")
# store_time("4시엔윤도현입니다", "5", "5315", "5323")
# store_time("4시엔윤도현입니다", "6", "5400", "5408")
# store_time("4시엔윤도현입니다", "7", "7025", "7032")

# # # # # 3. 고정음성을 등록한다.
# fix_sound_path_1 = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/brunchcafe/230508/fixed_wav/fixed_1.wav"
# fix_sound_path_2 = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/brunchcafe/230508/fixed_wav/fixed_2.wav"
# fix_sound_path_3 = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/brunchcafe/230508/fixed_wav/fixed_3.wav"
# fix_sound_path_4 = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/brunchcafe/230508/fixed_wav/fixed_4.wav"
# fix_sound_path_5 = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/brunchcafe/230508/fixed_wav/fixed_5.wav"
# program_name = 'brunchcafe'
# fix_sound_name_1 = 'start'
# fix_sound_name_2 = 'part1_start'
# fix_sound_name_3 = 'mbc'
# fix_sound_name_4 = 'part2_start'
# fix_sound_name_5 = 'finish'
# register_song(fix_sound_path_1, program_name, fix_sound_name_1)
# register_song(fix_sound_path_2, program_name, fix_sound_name_2)
# register_song(fix_sound_path_3, program_name, fix_sound_name_3)
# register_song(fix_sound_path_4, program_name, fix_sound_name_4)
# register_song(fix_sound_path_5, program_name, fix_sound_name_5)

# fix_sound_path_1 = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/MBC FM4U/yb/2023-06-18/fixed_wav/_1.wav"
# fix_sound_path_2 = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/MBC FM4U/yb/2023-06-18/fixed_wav/_2.wav"
# fix_sound_path_3 = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/MBC FM4U/yb/2023-06-18/fixed_wav/_3.wav"
# fix_sound_path_4 = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/MBC FM4U/yb/2023-06-18/fixed_wav/_4.wav"
# fix_sound_path_5 = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/MBC FM4U/yb/2023-06-18/fixed_wav/_5.wav"
# fix_sound_path_6 = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/MBC FM4U/yb/2023-06-18/fixed_wav/_6.wav"
# fix_sound_path_7 = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/MBC FM4U/yb/2023-06-18/fixed_wav/_7.wav"
# program_name = '4시엔윤도현입니다'
# fix_sound_name_1 = '1'
# fix_sound_name_2 = '2'
# fix_sound_name_3 = '3'
# fix_sound_name_4 = '4'
# fix_sound_name_5 = '5'
# fix_sound_name_6 = '6'
# fix_sound_name_7 = '7'
# register_song(fix_sound_path_1, program_name, fix_sound_name_1)
# register_song(fix_sound_path_2, program_name, fix_sound_name_2)
# register_song(fix_sound_path_3, program_name, fix_sound_name_3)
# register_song(fix_sound_path_4, program_name, fix_sound_name_4)
# register_song(fix_sound_path_5, program_name, fix_sound_name_5)
# register_song(fix_sound_path_6, program_name, fix_sound_name_6)
# register_song(fix_sound_path_7, program_name, fix_sound_name_7)


# # 4. 주어진 메인 음성을 split한다.
# import time

# song_path = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/brunchcafe/230508/raw.wav"
# program_name = "brunchcafe"
# save_path = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/brunchcafe/230508/split_wav"
# start_time = time.time()
# start_split(song_path, program_name, save_path)
# end_time = time.time()
# print("Elapsed time:", end_time - start_time, "seconds")

import time

song_path = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/MBC FM4U/yb/2023-06-18/raw.wav"
program_name = "4시엔윤도현입니다"
save_path = "/Users/jinjiwon/VisualRadio/VisualRadio/radio_storage/MBC FM4U/yb/2023-06-18/split_wav"
start_time = time.time()
start_split(song_path, program_name, save_path)
end_time = time.time()
print("Elapsed time:", end_time - start_time, "seconds")
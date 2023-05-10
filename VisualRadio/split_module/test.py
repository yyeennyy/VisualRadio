from register import *
from fingerprint import *
import settings
from DB.setup_db import setup_db
from DB.fix_db import setup_fix_db
from recognise import *
from split import *

# # # 1. db를 생성한다.
setup_db()
setup_fix_db()

# # # # 2. 고정음성의 대략적인 시간대를 입력한다.
# # # # store_time(라디오 프로그램 이름, 고정음성 이름, 시작시간(s), 종료시간(s), 순서)
store_time("brunchcafe", "start", "6", "15")
store_time("brunchcafe", "part1_start", "660", "720")
store_time("brunchcafe", "mbc", "1715", "1740")
store_time("brunchcafe", "part2_start", "1770", "1835")
store_time("brunchcafe", "finish", "3360", "3480")

# # # # 3. 고정음성을 등록한다.
fix_sound_path_1 = r".\VisualRadio\radio_storage\brunchcafe\230226\fixed_wav\fixed_1.wav"
fix_sound_path_2 = r".\VisualRadio\radio_storage\brunchcafe\230226\fixed_wav\fixed_2.wav"
fix_sound_path_3 = r".\VisualRadio\radio_storage\brunchcafe\230226\fixed_wav\fixed_3.wav"
fix_sound_path_4 = r".\VisualRadio\radio_storage\brunchcafe\230226\fixed_wav\fixed_4.wav"
fix_sound_path_5 = r".\VisualRadio\radio_storage\brunchcafe\230226\fixed_wav\fixed_5.wav"
program_name = 'brunchcafe'
fix_sound_name_1 = 'start'
fix_sound_name_2 = 'part1_start'
fix_sound_name_3 = 'mbc'
fix_sound_name_4 = 'part2_start'
fix_sound_name_5 = 'finish'
register_song(fix_sound_path_1, program_name, fix_sound_name_1)
register_song(fix_sound_path_2, program_name, fix_sound_name_2)
register_song(fix_sound_path_3, program_name, fix_sound_name_3)
register_song(fix_sound_path_4, program_name, fix_sound_name_4)
register_song(fix_sound_path_5, program_name, fix_sound_name_5)


# # 4. 주어진 메인 음성을 split한다.
# # import time

# # song_path = r"D:\JP\Server\VisualRadio\radio_storage\brunchcafe\230226\raw.wav"
# # program_name = "이석훈의 브런치카페"
# # save_path = r"D:\JP\Server\VisualRadio\radio_storage\brunchcafe\230226\split_wav"
# # start_time = time.time()
# # split(song_path, program_name, save_path)
# # end_time = time.time()
# # print("Elapsed time:", end_time - start_time, "seconds")


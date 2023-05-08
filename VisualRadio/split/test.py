from register import *
from fingerprint import *
import settings
from DB.setup_db import setup_db
from DB.fix_db import setup_fix_db
from recognise import *
from split import *

# # 1. db를 생성한다.
# setup_db()
# setup_fix_db()

# # # 2. 고정음성의 대략적인 시간대를 입력한다.
# # # store_time(라디오 프로그램 이름, 고정음성 이름, 시작시간(s), 종료시간(s), 순서)
# store_time("이석훈의 브런치카페", "start", "6", "15")
# store_time("이석훈의 브런치카페", "part1_start", "660", "720")
# store_time("이석훈의 브런치카페", "mbc", "1715", "1740")
# store_time("이석훈의 브런치카페", "part2_start", "1770", "1835")
# store_time("이석훈의 브런치카페", "finish", "3360", "3480")

# # 3. 고정음성을 등록한다.
# fix_sound_path_1 = '/Users/singyeongjun/Desktop/graduation_project/test/fix_sound/start.wav'
# fix_sound_path_2 = '/Users/singyeongjun/Desktop/graduation_project/test/fix_sound/part1_start.wav'
# fix_sound_path_3 = '/Users/singyeongjun/Desktop/graduation_project/test/fix_sound/mbc.wav'
# fix_sound_path_4 = '/Users/singyeongjun/Desktop/graduation_project/test/fix_sound/part2_start.wav'
# fix_sound_path_5 = '/Users/singyeongjun/Desktop/graduation_project/test/fix_sound/finish.wav'
# program_name = '이석훈의 브런치카페'
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


# 4. 주어진 메인 음성을 split한다.
song_path = "/Users/singyeongjun/Desktop/graduation_project/test/main_sound/radio_20230501.wav"
program_name = "이석훈의 브런치카페"
save_path = "/Users/singyeongjun/Desktop/graduation_project/test/split_sound"
split(song_path, program_name, save_path)
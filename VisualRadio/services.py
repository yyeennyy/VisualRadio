# Business Logic Layer(비즈니스 로직 계층)
# 애플리케이션의 비즈니스 로직을 담당하는 계층입니다.
# Presentation Layer에서 전달된 데이터를 처리하고, 필요한 데이터를 데이터 저장 계층에서 조회합니다.


import os
########################## 수집기 관련 로직 ##########################

# 저장 로직
def save_wav(wav, radio_url):
    # wav 검증
    # 

    # wav를 radio_url에 저장
    with open(radio_url, 'wb') as f:
        f.write(wav)

    # 처리 결과 리턴
    #


# 로직 1 : raw.wav를 분할한다.
def split(radio_name, date):
    radio_url = storage_path(radio_name, date)
    raw_url = f'{radio_url}\\raw.wav'
    fixed_url = f'{radio_url}\\fixed_wav'

    # fixed_wav 폴더에 있는 고정음성을 이용하여 분할한다.
    # 분할 로직 ##############
    #
    #
    # 분할 완료 후 db 업데이트
    #
    #########################


    # 분할 결과를 검증한다.
    # 분할 개수를 리턴한다.    
    n = 3  # section 개수
    return n



# 일단 예정 없음
# def find_target():
    # stt 대상을 찾는다 (멘트)
    # 이 라디오 포맷 정보를 참고한다.



# 로직2
def stt(radio_name, date):
    # 모든 section 결과를 무조건 stt한다.
    radio_url = storage_path(radio_name, date)
    section_dir = f'{radio_url}\\split_wav'
    section_list = os.listdir(section_dir)
    print( section_dir + "\\" + section_list[0])

    # TODO: 섹션마다 stt 처리하기
    for section in section_list:
        # stt 로직 ############# 
        # 'time'다음줄에 'text'가 오도록 결과물 만들기
        file_path = section_dir + "\\" + section
        #
        # stt 구현
        #
        print(f'stt완료 (섹션: {section})')
        #######################
    # # stt가 완료되어, section마다 stt_1, stt_2, stt_3, ...이 만들어진 상태다.
    


# 로직3
def make_txt(radio_name, date):
    # raw_txt 폴더에 stt결과가 있는지 검증
    # 존재하는 stt_1, stt_2, ... 중에서 컨텐츠화 가능한 것들
    target_list = find_contents(radio_name, date)

    # 컨텐츠화 로직 ###########
    #
    #
    # txt_contents에 저장
    ##########################


def find_contents(radio_name, date):
    stt_dir = storage_path(radio_name, date)
    stt_list = os.listdir(stt_dir + '\\raw_stt')
    stt_list.remove('stt_all.txt')
    # - text 길이를 고려해 target을 찾으면 좋을 듯?
    for stt_name in stt_list:
        file_path = os.path.join(stt_dir, stt_name)
        # stt 내용 조회
        with open(file_path, 'r') as f:
            stt_content = f.read()
            # 처리 로직 구현
            #
            #
            # ↓ target일 경우
            target_list.add(stt_name)

    target_list = ['stt_2', 'stt_3']  # 예시 : stt_2, stt_3는 컨텐츠화 가능한 stt결과
    return target_list  


#####################
def storage_path(radio_name, radio_date):
    return os.getcwd() + '\\VisualRadio\\radio_storage\\' + radio_name + '\\' + radio_date


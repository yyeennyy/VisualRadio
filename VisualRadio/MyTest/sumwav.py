import wave
import os

def sum_wav_sections(broadcast, name, date):
    path = f"./VisualRadio/radio_storage/{broadcast}/{name}/{date}"
    src_path = path + "/split_wav"
    dst_path = path + "/sum.wav"

    src_files = os.listdir(src_path)

    input_streams = []
    for src in src_files:
        input_streams.append(wave.open(src_path + "/" + src, 'rb'))
    # 첫 번째 입력 파일의 정보를 가져옵니다.
    params = input_streams[0].getparams()
    # 출력 파일을 열고 쓰기 모드로 처리합니다.
    output_stream = wave.open(dst_path, 'wb')
    # 출력 파일의 파라미터를 설정합니다.
    output_stream.setparams(params)
    # 입력 파일을 읽고 출력 파일에 작성합니다.
    for input_stream in input_streams:
        output_stream.writeframes(input_stream.readframes(input_stream.getnframes()))
    # 파일을 닫습니다.
    for input_stream in input_streams:
        input_stream.close()
    output_stream.close()
    print("이어붙이기가 완료되었습니다.")


sum_wav_sections('MBC', 'brunchcafe', '2023-05-08')
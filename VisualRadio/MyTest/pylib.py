import speech_recognition as sr
from pydub import AudioSegment
import wave

def split_audio(file_path, interval):
    r = sr.Recognizer()

    # 음성 파일 로드 및 변환
    audio = AudioSegment.from_file(file_path)
    with wave.open(file_path, 'rb') as wav_file:
      sample_rate = wav_file.getframerate()  # 샘플 레이트
      num_frames = wav_file.getnframes()  # 프레임 수
      duration = num_frames / sample_rate  # 실제 음성 파일의 길이 (초 단위)

    print("du:", duration / 60)
    # 구간의 시작 및 끝 시간 계산
    start_time = 0
    end_time = start_time + interval * 1000  # 구간의 길이 (밀리초 단위)

    while end_time <= len(audio):
        try:
          # 구간 추출
          audio_segment = audio[start_time:end_time]

          # 추출된 구간을 임시 파일로 저장 (옵션)
          temp_file_path = "temp.wav"
          audio_segment.export(temp_file_path, format="wav")

          # 음성 인식 수행
          with sr.AudioFile(temp_file_path) as temp_audio_file:
              temp_audio_data = r.record(temp_audio_file)
              text = r.recognize_google(temp_audio_data, language='ko-KR')

          # 추출된 구간의 텍스트 출력 또는 원하는 로직 수행
          print(f"구간 {start_time / 1000} - {end_time / 1000}: {text}")

          # 임시 파일 삭제 (옵션)
          # import os
          # os.remove(temp_file_path)
        except:
            pass

        # 다음 구간으로 이동
        start_time = end_time
        end_time += interval * 1000

    # 마지막 구간 처리
    if start_time < len(audio):
        audio_segment = audio[start_time:]

        # 추출된 구간을 임시 파일로 저장 (옵션)
        temp_file_path = "temp.wav"
        audio_segment.export(temp_file_path, format="wav")

        # 음성 인식 수행
        with sr.AudioFile(temp_file_path) as temp_audio_file:
            temp_audio_data = r.record(temp_audio_file)
            text = r.recognize_google(temp_audio_data)

        # 추출된 구간의 텍스트 출력 또는 원하는 로직 수행
        print(f"구간 {start_time / 1000} - {len(audio) / 1000}: {text}")

        # 임시 파일 삭제 (옵션)
        import os
        os.remove(temp_file_path)

# 사용 예시
file_path = r'C:\Users\kye33\Desktop\VisualRadio\VisualRadio\MyTest\sec_1.wav'
interval = 10  # 구간의 길이 (초 단위)
split_audio(file_path, interval)



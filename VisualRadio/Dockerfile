FROM python:3.8.17-slim-buster as builder

WORKDIR /app
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y git
RUN apt update && apt-get install -y python3-pip
RUN apt-get install -y ffmpeg
RUN apt-get install flac

RUN apt-get install -y default-jdk default-jre

RUN pip3 install git+https://github.com/openai/whisper.git

RUN pip install typer==0.3.2
RUN pip install flask==2.0.0
RUN pip install click==7.1.2
RUN pip install typer==0.3.2
RUN pip install flask==2.0.0
## tensorflow version ######################
RUN pip install tensorflow==2.12.0
############################################
RUN pip install spleeter==2.3.2
RUN pip install Flask-Caching==2.0.2
RUN pip install Flask-Cors==4.0.0
RUN pip install pymysql==1.1.0
RUN pip install flask_sqlalchemy==2.5.0
RUN pip install black==20.8b0
# torch version ############################
RUN pip install torch==2.0.0+cu118 torchvision==0.15.1+cu118 torchaudio==2.0.1 --index-url https://download.pytorch.org/whl/cu118
############################################
RUN pip install cryptography==41.0.3
RUN pip install setuptools-rust==1.6.0
RUN pip install SpeechRecognition==3.10.0
RUN pip install natsort==8.4.0
RUN pip install librosa==0.8.1
RUN pip install pydub==0.25.1
RUN pip install protobuf==3.20.3
RUN pip install pandas==1.5.3
RUN pip install matplotlib==3.7.2
RUN pip install psutil==5.9.5
RUN pip install konlpy==0.6.0
RUN pip install sqlalchemy==1.4
RUN pip uninstall numpy -y
RUN pip install numpy --upgrade
RUN pip install numba==0.55.2
RUN pip install gensim==3.4.0
RUN pip install transformers
RUN pip install google-api-python-client
RUN pip install googletrans==4.0.0-rc1
RUN pip install faster-whisper

# 두 번째 스테이지: 최종 이미지 설정
FROM python:3.8.17-slim-buster

# 첫 번째 스테이지에서 설치한 필요한 패키지들 복사
COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages

# 작업 디렉토리 설정
WORKDIR /app

RUN apt update && apt-get install -y python3-pip
RUN apt-get install -y ffmpeg
RUN apt-get install flac

RUN apt-get install -y default-jdk default-jre

EXPOSE 5001

CMD [ "python", "main.py"]
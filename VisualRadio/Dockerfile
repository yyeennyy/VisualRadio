FROM python:3.8-buster

RUN apt update && apt-get install -y python3-pip
RUN pip install --upgrade pip
RUN apt-get install -y ffmpeg
RUN apt-get install flac

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN pip install flask==2.0.0 click==7.1.2 black sqlalchemy Flask-Caching Flask-Cors flask_sqlalchemy pymysql
RUN pip install SQLAlchemy==1.4
RUN pip install pymysql
RUN pip install torch
RUN pip install spleeter==2.4.0
RUN pip install tensorflow==2.9.0
RUN pip install cryptography
RUN pip3 install setuptools-rust
RUN pip install SpeechRecognition
RUN pip install natsort
RUN pip install librosa
RUN pip install pydub
RUN pip install protobuf==3.9.2
RUN pip install pandas
RUN pip install matplotlib
RUN pip install psutil
RUN pip install konlpy
RUN pip3 install git+https://github.com/openai/whisper.git

# installing java jdk and java jre
RUN apt-get install -y default-jdk default-jre

EXPOSE 5001

CMD [ "python", "main.py" ]

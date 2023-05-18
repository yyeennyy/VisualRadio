FROM python:3.10-buster

RUN apt update && apt-get install -y python3-pip
RUN pip install --upgrade pip
RUN apt-get install -y ffmpeg
RUN apt-get update
RUN apt-get install flac

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip install cryptography
# RUN pip3 install setuptools-rust
# RUN pip3 install git+https://github.com/openai/whisper.git
RUN pip install SpeechRecognition
RUN pip install natsort
RUN pip install librosa


EXPOSE 5001

CMD [ "python", "main.py" ]

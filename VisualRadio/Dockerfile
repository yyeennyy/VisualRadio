FROM python:3.8.17-buster

RUN apt update && apt-get install -y python3-pip
RUN pip install --upgrade pip
RUN apt-get install -y ffmpeg
RUN apt-get install flac

WORKDIR /app

# RUN pip install flask==2.0.0 click==7.1.2 sqlalchemy Flask-Caching Flask-Cors flask_sqlalchemy pymysql
# RUN pip install black==22.1.0
# RUN pip install SQLAlchemy==1.4
# RUN pip install pymysql
# RUN pip install torch torchvision


# conda 설치
# RUN apt-get update && apt-get install -y wget
# RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh -O ~/miniconda.sh \
#     && bash ~/miniconda.sh -b -p /opt/conda \
#     && rm ~/miniconda.sh
# ENV PATH /opt/conda/bin:$PATH
# RUN conda install -c conda-forge python==3.8
# # TensorFlow 설치
# RUN conda install -y -c conda-forge tensorflow==2.5.0
# RUN pip install spleeter==2.4.0

# RUN pip install tensorflow==2.13.0
# RUN pip install spleeter==2.3.2
RUN pip install typer==0.3.2
RUN pip install flask==2.0.0
RUN pip install click==7.1.2
RUN pip install typer==0.3.2
RUN pip install flask==2.0.0
RUN pip install tensorflow==2.13.0
RUN pip install spleeter==2.3.2
RUN pip install Flask-Caching==2.0.2
RUN pip install Flask-Cors==4.0.0
RUN pip install pymysql==1.1.0
RUN pip install flask_sqlalchemy==2.5.0
RUN pip install black==20.8b0
RUN pip install torch==2.0.1
RUN pip install torchvision==0.15.2
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
# RUN apt install -y python3-numpy


# RUN pip install -r requirements.txt
# RUN pip3 install -r requirements.txt

# RUN pip3 install setuptools-rust
# RUN pip install SpeechRecognition
# RUN pip install natsort
# RUN pip install librosa
# RUN pip install pydub
# RUN pip install protobuf==3.9.2
# RUN pip install pandas
# RUN pip install matplotlib
# RUN pip install psutil
# RUN pip install konlpy
RUN pip3 install git+https://github.com/openai/whisper.git

# installing java jdk and java jre
RUN apt-get install -y default-jdk default-jre
# RUN pip install --upgrade numpy protobuf

# RUN pip uninstall -y numba
# RUN pip install -U numba

EXPOSE 5001

CMD [ "python", "main.py" ]

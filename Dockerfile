FROM python:3.10-buster

RUN apt update && apt-get install -y python3-pip
RUN pip install --upgrade pip
RUN apt-get install -y ffmpeg

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip install cryptography

EXPOSE 5000

CMD [ "python", "VisualRadio/app.py" ]
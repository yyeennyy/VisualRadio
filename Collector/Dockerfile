FROM python:3.8-alpine

WORKDIR /Collector
COPY . .

RUN chmod +x ./radio.sh

# 아래서 apsheduler를 pip install하려면 gcc가 필요함 -> build-base가 필요함 (빌드 도구)
RUN apk add build-base 

RUN apk add --update py-pip

RUN apk update && apk add ffmpeg

# 필요한 것 설치하기!
# RUN pip install ... 
RUN pip install --upgrade pip
RUN pip3 install apscheduler


CMD [ "python", "./Client.py" ]
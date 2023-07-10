FROM python:3.8-buster

RUN apt update && apt-get install -y python3-pip
RUN pip install --upgrade pip

WORKDIR /collector
COPY . .

# 필요한 것 설치하기!
# RUN pip install ... 
#

CMD [ "python", "Client.py" ]
# base 이미지
FROM python:3.10-buster

RUN apt update && apt-get install -y python3-pip
RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python", "VisualRadio/app.py" ]
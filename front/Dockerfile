FROM node:18.17.1-slim

WORKDIR /app

# package.json 워킹 디렉토리에 복사 (.은 설정한 워킹 디렉토리를 뜻함)
COPY package.json .
# 명령어 실행 (의존성 설치)
RUN npm install
RUN npm i react-router-dom
RUN npm install axios

# RUN npm install --save react-helmet

EXPOSE 3000

CMD ["npm", "start"]
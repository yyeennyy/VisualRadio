#Build stage
FROM gradle:latest AS BUILD
WORKDIR /Collector
COPY . . 
RUN gradle build
# Package stage
FROM openjdk:17-alpine
ENV JAR_NAME=Client.jar
ENV APP_HOME=/Collector
WORKDIR $APP_HOME
COPY --from=BUILD $APP_HOME .

COPY manifest.txt /META-INF/MANIFEST.MF
# RUN chmod +x ./gradlew
# RUN ./gradlew build
RUN apk update && apk add --no-cache busybox-extras
RUN apk update && apk add ffmpeg
# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

CMD ["java", "-jar", "build/libs/Client.jar"]
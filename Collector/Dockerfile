#Build stage
FROM gradle:latest AS BUILD
WORKDIR /Collector
COPY . . 
RUN gradle build

# Package stage
FROM openjdk:17-buster
ENV JAR_NAME=Client.jar
ENV APP_HOME=/Collector
WORKDIR $APP_HOME
COPY --from=BUILD $APP_HOME .

COPY manifest.txt /META-INF/MANIFEST.MF
RUN apt-get update && apt-get install -y busybox ffmpeg


# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apt-get install -y python3 python3-pip
RUN pip3 install --no-cache --upgrade pip setuptools

CMD ["java", "-jar", "build/libs/Client.jar"]
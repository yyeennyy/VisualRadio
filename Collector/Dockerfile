FROM openjdk:17

WORKDIR /Collector

COPY . .
COPY gradlew .
COPY gradle ./gradle


RUN chmod +x ./gradlew
RUN ./gradlew clean build

CMD ["java", "-jar", "build/libs/Client.jar"]
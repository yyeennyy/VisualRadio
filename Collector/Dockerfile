#Build stage
FROM gradle:latest AS BUILD
WORKDIR /Collector
COPY . . 
RUN gradle build
# Package stage
FROM openjdk:17
ENV JAR_NAME=Client.jar
ENV APP_HOME=/Collector
WORKDIR $APP_HOME
COPY --from=BUILD $APP_HOME .

COPY manifest.txt /META-INF/MANIFEST.MF
RUN chmod +x ./gradlew
RUN ./gradlew build

CMD ["java", "-jar", "build/libs/Client.jar"]
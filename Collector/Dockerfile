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

# RUN chmod +x ./gradlew
# WORKDIR /Collector
# RUN ./gradlew clean build
EXPOSE 8080
ENTRYPOINT exec java -jar $APP_HOME/build/libs/$JAR_NAME 
# CMD ["java", "-jar", "build/libs/Client.jar"]
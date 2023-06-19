FROM openjdk:17

WORKDIR /Collector

COPY . .
COPY gradlew .
COPY gradle ./gradle
COPY manifest.txt /META-INF/MANIFEST.MF
# COPY mysql-connector-j-8.0.33.jar .
RUN chmod +x ./gradlew
RUN ./gradlew build

CMD ["java", "-jar", "build/libs/Client.jar"]
# CMD ["java", "app.jar:/app/mysql-connector-java.jar", "your.main.Class"]
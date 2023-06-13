FROM openjdk:17

# 여기랑, settings.gradle의 root 디렉토리 이름이랑 일치해야 하네!?
WORKDIR /Collector

# Gradle Wrapper 파일과 설정 파일을 복사합니다.
COPY . .
COPY gradlew .
COPY gradle ./gradle


# Gradle Wrapper를 실행하여 의존성을 다운로드하고 애플리케이션을 빌드합니다.
RUN chmod +x ./gradlew
RUN ./gradlew clean build

# 애플리케이션을 실행합니다.
CMD ["java", "-jar", "build/libs/Client.jar"]
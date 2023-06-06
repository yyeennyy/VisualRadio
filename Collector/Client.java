package Collector;

import java.io.BufferedReader;
// import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.time.LocalTime;
import java.time.Duration;

public class Client {
    public static void main(String[] args) {
        LocalTime currentTime = LocalTime.now();
        LocalTime targetTime = LocalTime.of(23, 43); 
        long initialDelay = Duration.between(currentTime, targetTime).toSeconds();
        System.out.println(initialDelay);
        if (initialDelay < 0) {
            // 이미 오전 11시를 지난 경우, 다음날 오전 11시로 초기 지연을 계산
            initialDelay += Duration.ofDays(1).toSeconds();
        }
        ScheduledExecutorService executorService = Executors.newScheduledThreadPool(1);
        executorService.scheduleAtFixedRate(new recordRadio("test", "11:00"), 0, 24*60*60, TimeUnit.SECONDS);
    }

    // 실행할 작업 태스크
    public static class recordRadio implements Runnable {
        private String broadcast;
        private String start_time;
        
        public recordRadio(String broadcast, String start_time) {
            this.broadcast = broadcast;
            this.start_time = start_time;
        }

        public void run() {
            try {
                // POST 요청 보내기
                // URL url = new URL("http://localhost:5000");
                // URI uri = new URI("http://localhost/collector");
                URI uri = null;
                try {
                    uri = new URI("http://localhost/collector");
                } catch (URISyntaxException e) {
                    e.printStackTrace();
                }
                URL url = uri.toURL();
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setRequestProperty("Content-Type", "application/json;utf-8");
                connection.setRequestProperty("Accept","application/json");
                connection.setRequestMethod("POST");
                connection.setDoOutput(true);
                
                // 필요한 데이터 설정 (방송사, 예약 시간 등)
                // String requestBody = "broadcast=" + broadcast + "&start_time=" + start_time;
                String jsonStr = String.format("{\"broadcast\":\"%s\", \"start_time\":\"%s\"}", broadcast, start_time);

                // 요청 데이터 전송
                // try(OutputStream os = connection.getOutputStream()){
                //     byte[] input = jsonStr.getBytes("utf-8");
                //     os.write(input, 0, input.length);
                // }
                // try(BufferedReader br = new BufferedReader(new InputStreamReader(connection.getInputStream(),"utf-8"))){
                //     StringBuilder response = new StringBuilder();
                //     String responseLine = null;
                //     while((responseLine = br.readLine()) != null){
                //         response.append(responseLine.trim());
                //     }
                //     System.out.println(response.toString());
                // }
                OutputStream outputStream = connection.getOutputStream();
                outputStream.write(jsonStr.getBytes());
                outputStream.flush();
                outputStream.close();
                
                // 응답 받기
                int responseCode = connection.getResponseCode();
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    // 응답 데이터 받아오기
                    BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                    StringBuilder response = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        response.append(line);
                    }
                    reader.close();

                    // 응답 데이터 파싱하여 라디오 이름과 녹음 시간 얻기
                    // 응답 데이터 = "radio_name=@@$&record_len=@@"
                    // 응답 데이터 = {"radio_name": "brunchcafe", "record_len": 10}
                    String responseData = response.toString();
                    // System.out.println(responseData.getClass().getSimpleName()); // 변수 타입 확인
                    
                    String radio_name = parseResponseData(responseData, "radio_name");
                    int record_len = Integer.parseInt(parseResponseData(responseData, "record_len"));
                    System.out.println("[응답 받음] " + radio_name +" "+ String.valueOf(record_len));
                    
                    
                    // radio.bat 파일 실행
                    // ProcessBuilder processBuilder = new ProcessBuilder("cmd.exe", "/c", "./radio.bat", broadcast, radio_name, String.valueOf(record_len));
                    // String[] command = { "bash", "-c", "./radio.sh" };
                    // ProcessBuilder processBuilder = new ProcessBuilder(command);
                    // ProcessBuilder processBuilder = new ProcessBuilder("bash", "-c", "./radio.sh", broadcast, radio_name, String.valueOf(record_len));
                    // processBuilder.redirectErrorStream(true);
                    // Process process = processBuilder.start();

                    // String [] batFilePath = {"cmd.exe", "/c", "./radio.bat", broadcast, radio_name, String.valueOf(record_len)};
                    // Process process = Runtime.getRuntime().exec(batFilePath);
                    // ProcessBuilder processBuilder = new ProcessBuilder("cmd.exe", "/c", batFilePath, broadcast, radio_name, String.valueOf(record_len));
                    // processBuilder.directory(new File("/Users/jinjiwon/VisualRadio/VisualRadio"));
                    // processBuilder.redirectErrorStream(true);
                    // Process process = processBuilder.start();

                    // ProcessBuilder pwdProcessBuilder = new ProcessBuilder("pwd");
                    // Process pwdProcess = pwdProcessBuilder.start();
                    // int pwdExitCode = pwdProcess.waitFor();
                    // if (pwdExitCode == 0) {
                    //     System.out.println("permission!");
                    // } else {
                    //     System.out.println("fail!");
                    // }

                    // try {
                    //     // ProcessBuilder를 사용하여 명령어 실행
                    //     ProcessBuilder pwdProcessBuilder = new ProcessBuilder("pwd");
                    //     pwdProcessBuilder.redirectErrorStream(true);
                    //     Process pwdProcess = pwdProcessBuilder.start();

                    //     // 명령어 실행 결과 읽기
                    //     BufferedReader bReader = new BufferedReader(new InputStreamReader(pwdProcess.getInputStream()));
                    //     String tmp;
                    //     while ((tmp = bReader.readLine()) != null) {
                    //         System.out.println(tmp);
                    //     }
                    //     reader.close();

                    //     // 프로세스 종료 코드 확인
                    //     int exitCode = pwdProcess.waitFor();
                    //     System.out.println("Exit Code: " + exitCode);
                    // } catch (IOException | InterruptedException e) {
                    //     e.printStackTrace();
                    // }

                    // ProcessBuilder chmodProcessBuilder = new ProcessBuilder("chmod", "+x", "radio.sh");
                    // Process chmodProcess = chmodProcessBuilder.start();
                    // int chmodExitCode = chmodProcess.waitFor();
                    // if (chmodExitCode == 0) {
                    //     System.out.println("permission!");
                    // } else {
                    //     System.out.println("fail!");
                    // }
                    
                    // radio.sh 파일 실행
                    String os = System.getProperty("os.name").toLowerCase();
                    System.out.println(os);
                    ProcessBuilder processBuilder;

                    if (os.contains("win")) {
                        processBuilder = new ProcessBuilder("cmd.exe", "/c", "./radio.bat", broadcast, radio_name, String.valueOf(record_len));
                    } else if (os.contains("mac")) {
                        processBuilder = new ProcessBuilder("/bin/sh", "./radio.sh", broadcast, radio_name, String.valueOf(record_len));
                    } else {
                        System.out.println("지원하지 않는 운영 체제입니다.");
                        return;
                    }

                    Process process = processBuilder.start();

                    // 프로세스가 완료될 때까지 대기
                    int exitCode = process.waitFor();
                    
                    System.out.println(exitCode);

                    // 프로세스 종료 코드 확인
                    if (exitCode == 0) {
                        System.out.println("radio.bat 파일 실행 완료");
                        System.out.println("time: " + start_time);
                        System.out.println("Broadcast: " + broadcast);
                        System.out.println("Radio Name: " + radio_name);
                        System.out.println("Recording Length: " + record_len);
                    } else {
                        System.out.println("radio.bat 파일 실행 실패");
                    }
                } else {
                    System.out.println("POST 요청 실패 - 응답 코드: " + responseCode);
                }
                connection.disconnect();
            } catch (IOException | InterruptedException e) {
                e.printStackTrace();
            }
        }

        private String parseResponseData(String responseData, String key) {
            // 응답 데이터를 파싱하여 특정 키의 값을 추출하는 로직 구현

            if (responseData == null) {
                return null;
            }
            responseData = responseData.replace("{", "");
            responseData = responseData.replace("}", "");

            String[] keyValuePairs = responseData.split(",");
            for (String pair : keyValuePairs) {
                pair = pair.replace("\"", "").replace("\\", "");
                String[] parts = pair.split(":");
                if (parts.length == 2 && parts[0].equals(key)) {
                    String value = parts[1];
                    // 따옴표 제거
                    value = value.replace("\"", "");
                    return value;
                }
            }

            // String[] keyValuePairs = responseData.split("&");

            // if (keyValuePairs != null) {
            //     for (String pair : keyValuePairs) {
            //         String[] parts = pair.split("=");
            //         if (parts.length == 2 && parts[0].equals(key)) {
            //             return parts[1];
            //         }
            //     }
            //     return null;
            // }
            return null;
        }
    }
}

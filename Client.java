import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class Client {
    public static void main(String[] args) {

        // ScheduledExecutorService 생성
        ScheduledExecutorService executorService = Executors.newScheduledThreadPool(1);
        // 작업을 동시에 실행할 경우 괄호 안에 작업 개수를 넣어주면 됨 ex) 2
        // ScheduledExecutorService executorService = Executors.newScheduledThreadPool(2);
        
        // 작업 스케줄링
        executorService.scheduleAtFixedRate(new recordRadio("MBCfm4u", "17:10"), 0, 24, TimeUnit.HOURS);
        // 작업 추가할 경우, 아래에 추가하면 됨
        // executorService.scheduleAtFixedRate(new recordRadio("MBC", "12:00"), 0, 24, TimeUnit.HOURS);
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
                URL url = new URL("http://localhost/collector");
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
                    String responseData = response.toString();
                    String radio_name = parseResponseData(responseData, "radio_name");
                    int record_len = Integer.parseInt(parseResponseData(responseData, "record_len"));

                    // radio.bat 파일 실행
                    ProcessBuilder processBuilder = new ProcessBuilder("cmd.exe", "/c", "radio.bat", broadcast, radio_name, String.valueOf(record_len));
                    processBuilder.redirectErrorStream(true);
                    Process process = processBuilder.start();

                    // 프로세스가 완료될 때까지 대기
                    int exitCode = process.waitFor();

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

            String[] keyValuePairs = responseData.split("&");

            if (keyValuePairs != null) {
                for (String pair : keyValuePairs) {
                    String[] parts = pair.split("=");
                    if (parts.length == 2 && parts[0].equals(key)) {
                        return parts[1];
                    }
                }
                return null;
            }
            return null;
        }
    }
}

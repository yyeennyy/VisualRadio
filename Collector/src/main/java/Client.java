// package Collector.src.main.java;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.file.Paths;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.time.LocalTime;
import java.time.Duration;
import org.json.JSONObject;
import java.util.logging.Logger;


public class Client {

    public static void main(String[] args) {
        // LocalTime currentTime = LocalTime.now();
        // LocalTime targetTime = LocalTime.of(23, 25); 
        // long initialDelay = Duration.between(currentTime, targetTime).toSeconds();

        // if (initialDelay < 0) {
        //     // 이미 오전 11시를 지난 경우, 다음날 오전 11시로 초기 지연을 계산
        //     initialDelay += Duration.ofDays(1).toSeconds();
        // }

        // System.out.printf("[collector] %d초 이후에 작동 시작\n", initialDelay);

        // ScheduledExecutorService executorService = Executors.newScheduledThreadPool(1);
        // executorService.scheduleAtFixedRate(new recordRadio("MBC FM4U", "23:25"), initialDelay, 24*60*60, TimeUnit.SECONDS);

        String broadcast = "MBC FM4U";

        LocalTime currentTime = LocalTime.now();
        // 테스트시 이 시간정보랑 radio 테이블의 start_time정보랑 일치해야 한다
        String[] h_m = String.valueOf(currentTime).split(":");
        int h = Integer.parseInt(h_m[0]);
        int m = Integer.parseInt(h_m[1]);
        LocalTime targetTime = LocalTime.of(h, (m+1) % 60);
        System.out.println(String.valueOf(targetTime));

        // 테스트용 시간 설정
        MySQLConnector connector = new MySQLConnector();
        String query = String.format("UPDATE radio SET start_time='%s' WHERE radio_name='brunchcafe'", targetTime, broadcast);
        System.out.println(query);
        connector.executeUpdateQuery(query);

        long initialDelay = Duration.between(currentTime, targetTime).toSeconds();
        if (initialDelay < 0) {
            // 설정한 시간까지 남은 대기시간 계산!
            initialDelay += Duration.ofDays(1).toSeconds();
        }
        System.out.printf("[collector] %d초 이후에 작동 시작\n", initialDelay);

        ScheduledExecutorService executorService = Executors.newScheduledThreadPool(1);
        // 테스트용 설정: visual-radio 컨테이너가 충분히 켜질 시간을 준다: 15초로 설정
        executorService.scheduleAtFixedRate(new recordRadio(broadcast, String.valueOf(targetTime)), initialDelay, 24*60*60, TimeUnit.SECONDS);
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
            // 필요한 데이터 설정 (방송사, 예약 시간 등)
            MySQLConnector connector = new MySQLConnector();
            String query = String.format("select * from radio WHERE broadcast='%s' and start_time='%s'", broadcast, start_time);
            System.out.println(query);
            String[] arr = connector.executeUpdateQuery(query);
            String radio_name = arr[0];
            String record_len = arr[1];
            System.out.println(radio_name + " " + record_len);


            ProcessBuilder chmodProcessBuilder = new ProcessBuilder("chmod", "+x", "radio.sh");
            Process chmodProcess;
            try {
                chmodProcess = chmodProcessBuilder.start();
                int chmodExitCode = chmodProcess.waitFor();
                if (chmodExitCode == 0) {
                    System.out.println("permission!");
                } else {
                    System.out.println("fail!");
                }
            } catch (IOException e) {
                e.printStackTrace();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            
            // radio.sh 파일 실행
            String os = System.getProperty("os.name").toLowerCase();
            System.out.println(os);
            ProcessBuilder processBuilder;

            if (os.contains("win")) {
                processBuilder = new ProcessBuilder("cmd.exe", "/c", "./radio.bat", broadcast, radio_name, String.valueOf(record_len));
            } else if (os.contains("mac") || os.contains("linux")) {
                processBuilder = new ProcessBuilder("dos2unix", "radio.sh");
                try {
                    processBuilder.start().waitFor();
                    System.out.println("리눅스 개행으로 바꿈");
                    String currentPath = Paths.get("").toAbsolutePath().toString();
                    System.out.println(currentPath);
                } catch (InterruptedException | IOException e) {
                    e.printStackTrace();
                } 
                String[] command = { "sh", "-x", "radio.sh", broadcast, radio_name, String.valueOf(record_len)};
                processBuilder = new ProcessBuilder(command);
            } else {
                System.out.println("지원하지 않는 운영 체제입니다.");
                return;
            }

            Process process;
            try {
                process = processBuilder.start();
                    
                // BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                // String line;
                // while ((line = errorReader.readLine()) != null) {
                //     System.out.println(line); // 오류 메시지를 터미널에 출력합니다.
                // }
                // 프로세스가 완료될 때까지 대기
                int exitCode = process.waitFor();
                
                System.out.println(exitCode);

                // 프로세스 종료 코드 확인
                if (exitCode == 0) {
                    System.out.println("radio.sh 파일 실행 완료");
                    System.out.println("time: " + start_time);
                    System.out.println("Broadcast: " + broadcast);
                    System.out.println("Radio Name: " + radio_name);
                    System.out.println("Recording Length: " + record_len);
                } else {
                    System.out.println("radio.bat 파일 실행 실패");
                }
            } catch (IOException e) {
                e.printStackTrace();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

        }
    }
}

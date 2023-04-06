import java.net.HttpURLConnection;
import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Client {

    static String server = "http://localhost:5000";

    // args 예시 : java Client arg1 arg2 arg3 ...
    // 인자 가정 : radio_name, radio_date, record_url, sampleRate

    public static void main(String[] args) throws Exception {

        // 파라미터
        // String radio_name = args[0];

        // 가장 먼저 수집기 작동
        // 배치파일 실행
        // TODO:  VisualRadio/radio_storage/radio_name/radio_date/raw.wav로 저장
        try {
            // D:\JP\Server\radio.bat
            Process p = Runtime.getRuntime().exec(".\\radio.bat");
        } catch (Exception e) {
            System.err.println(e);
        }
        // 저장 검증

        // TODO: wav 전처리
        //
        

        // ------------------ 서버에 요청 시작 ----------------
        // String api;
        // URL url;
        // HttpURLConnection con;
        // int responseCode;

        // ▼ 볼 필요 X
        // // 서버에 요청1 : raw.wav로 저장 요청
        // api = server + "/save_wav";
        // url = new URL(api);
        // con = (HttpURLConnection) url.openConnection();
        // con.setRequestMethod("GET");
        // responseCode = con.getResponseCode();
        // System.out.println("Response Code : " + responseCode);


        // 서버에 요청2 : 저장된 wav 처리 요청
        // api = server + "/start"; 
        // url = new URL(api);
        // con = (HttpURLConnection) url.openConnection(); 
        // con.setRequestMethod("GET");
        // responseCode = con.getResponseCode();
        // System.out.println("Response Code : " + responseCode);



        // 응답 내용 읽기
        // BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
        // String inputLine;
        // StringBuffer response = new StringBuffer();
        // while ((inputLine = in.readLine()) != null) {
        //     response.append(inputLine);
        // }
        // in.close();
        // // 응답 내용 출력
        // System.out.println("Response : " + response.toString());
    }


}

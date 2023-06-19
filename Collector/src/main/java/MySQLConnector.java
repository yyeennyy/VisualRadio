import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class MySQLConnector {
    private static final String DB_URL = "jdbc:mysql://mysql:3306/radio";
    private static final String USERNAME = "visualradio";
    private static final String PASSWORD = "visualradio";

    public String[] executeUpdateQuery(String query) {
        Connection connection = null;
        PreparedStatement preparedStatement = null;

        try {
            // 1. 드라이버 로딩
            Class.forName("com.mysql.cj.jdbc.Driver");

            // 2. 데이터베이스 연결
            connection = DriverManager.getConnection(DB_URL, USERNAME, PASSWORD);

            // 3. 쿼리 실행
            preparedStatement = connection.prepareStatement(query);


            boolean hasResultSet = preparedStatement.execute();
            System.out.println("쿼리가 실행되었습니다.");

            if (hasResultSet) {
                ResultSet resultSet = preparedStatement.getResultSet();
                String radio_name = "";
                String record_len = "";
                while (resultSet.next()) {
                    radio_name = resultSet.getString("radio_name");
                    record_len = resultSet.getString("record_len");
                }
                resultSet.close();
                return new String[]{radio_name, record_len};

            } else {
                preparedStatement.executeUpdate();
                return null;
            }
        } catch (SQLException | ClassNotFoundException e) {
            e.printStackTrace();
        } finally {
            // 4. 연결과 리소스 닫기
            try {
                if (preparedStatement != null)
                    preparedStatement.close();
                if (connection != null)
                    connection.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        return null;
    }
}
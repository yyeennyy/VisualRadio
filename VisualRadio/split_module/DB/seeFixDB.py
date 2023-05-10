
import sqlite3

# SQLite 데이터베이스에 연결
conn = sqlite3.connect('fix.db')
c = conn.cursor()

print('## 데이터베이스에 있는 테이블 이름 조회')
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()  # 모든 테이블 이름을 가져옴

# 테이블 이름 출력 또는 처리
for table in tables:
    print(table[0])  # 예시: 각 테이블 이름을 출력하는 경우

# 데이터 조회를 위한 SQL 질의 실행
c.execute('SELECT * FROM fix_time')  # 'table_name'은 실제 데이터베이스 테이블명에 대체되어야 합니다.
rows = c.fetchall()  # 모든 결과를 한 번에 가져옴

print('\n## 테이블 fix_time의 컬럼 정보')
c.execute("PRAGMA table_info(fix_time)")  # 'table_name'은 실제 데이터베이스 테이블명에 대체되어야 합니다.
columns = c.fetchall()  # 모든 컬럼 정보를 가져옴

# 조회된 컬럼 종류 출력 또는 처리
for column in columns:
    print(column[1])

print('\n## 테이블 fix_time의 데이터')
for row in rows:
    print(row)  # 예시: 각 행의 데이터를 출력하는 경우


# 연결 종료
conn.close()
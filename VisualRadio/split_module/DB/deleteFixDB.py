import sqlite3

con = sqlite3.connect('fix.db')
cur = con.cursor()

cur.execute("SELECT * FROM fix_time")
rows = cur.fetchall()

for row in rows:
    print(row)

con.close()

import sqlite3

# 데이터베이스 연결 생성
conn = sqlite3.connect("fix.db")

# 데이터베이스 내용 삭제
c = conn.cursor()
c.execute("DELETE FROM fix_time")

# 변경사항 저장
conn.commit()

# 데이터베이스 연결 닫기
conn.close()
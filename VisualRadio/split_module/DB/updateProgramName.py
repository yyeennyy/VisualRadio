import sqlite3

# --------- fix.db
con = sqlite3.connect('fix.db')
cur = con.cursor()

cur.execute("UPDATE fix_time SET program_name='이석훈의브런치카페' where program_name='brunchcafe'")
rows = cur.fetchall()

for row in rows:
    print(row)

con.commit()
con.close()

# --------- hash.db
con = sqlite3.connect('hash.db')
cur = con.cursor()

cur.execute("UPDATE song_info SET program_name='이석훈의브런치카페' where program_name='brunchcafe'")
rows = cur.fetchall()

for row in rows:
    print(row)

con.commit()
con.close()


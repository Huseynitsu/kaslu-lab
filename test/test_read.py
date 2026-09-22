import sqlite3

conn = sqlite3.connect("anammox.db")

cursor = conn.cursor()

cursor.execute(
    "SELECT * FROM experiments"
)

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
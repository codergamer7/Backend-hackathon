# create_database.py
import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    DOB TEXT NOT NULL,
    GENDER_L TEXT NOT NULL,
    TRN TEXT NOT NULL UNIQUE,
    STAFF_ID NOT NULL UNIQUE
)
''')

conn.commit()
conn.close()
print("✅ Database created.")

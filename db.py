import sqlite3

dbNAME = "tracker.db"

def initDB():
    conn = sqlite3.connect(dbNAME)
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS items (
                   itemID TEXT PRIMARY KEY,
                   name TEXT NOT NULL,
                   price INTEGER)
                   ''')
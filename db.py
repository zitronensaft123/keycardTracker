import sqlite3

dbNAME = "tracker.db"

def initDB():
    conn = sqlite3.connect(dbNAME)
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS items
                   (
                   itemID  PRIMARY KEY NOT NULL,
                   name TEXT NOT NULL,
                   price INTEGER
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS raids
                   (
                   raidID INTEGER PRIMARY KEY AUTOINCREMENT,
                   date TEXT NOT NULL,
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS foundItems
                   (
                   raid_ID INTEGER NOT NULL,
                   itemID   INTEGER NOT NULL,
                   quantity INTEGER,
                   PRIMARY KEY(raidID, itemID),
                   FOREIGN KEY(raidID) REFERENCES raids(raidID)
                   FOREIGN KEY(itemID) REFERENCES items(itemID)
                   )
                   ''')
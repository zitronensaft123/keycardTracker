import sqlite3
import api

dbNAME = "tracker.db"

conn = sqlite3.connect(dbNAME)
cursor = conn.cursor()

def initDB():

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS items
                   (
                   itemID TEXT PRIMARY KEY NOT NULL,
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
                   raid_ID  INTEGER NOT NULL,
                   itemID   TEXT NOT NULL,
                   quantity INTEGER,

                   PRIMARY KEY(raidID, itemID),
                   FOREIGN KEY(raidID) REFERENCES raids(raidID)
                   FOREIGN KEY(itemID) REFERENCES items(itemID)
                   )
                   ''')

def getTherapistPrice(item):
    for trader in item["traderPrices"]:
        if trader["trader"]["name"] == "Therapist":
            return (trader["price"])
        
    
def getHighestPrice(item):
    therapistPrice = getTherapistPrice(item)
    fleaPrice = item["avg24hPrice"]

    if therapistPrice is None:
        return fleaPrice
    elif fleaPrice is None:
        return
    elif fleaPrice > therapistPrice:
        return fleaPrice
    else:
        return therapistPrice

def updatePrices():
    items = api.getItemData()

    cursor.execute("INSERT INTO items (itemID, name, price) VALUES (?, ?, ?)", (items["Physical Bitcoin"]["id"], items["Physical Bitcoin"]["name"], getHighestPrice(items["Physical Bitcoin"])))
    
    cursor.execute("SELECT *")

    print(cursor.fetchall)

updatePrices()
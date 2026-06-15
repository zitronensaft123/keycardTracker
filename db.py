import sqlite3
import api
from datetime import datetime
from datetime import timedelta

dbNAME = "tracker.db"
price = 900000

conn = sqlite3.connect(dbNAME)
cursor = conn.cursor()

# list of tracked items
trackedITEMS = [
    "Physical Bitcoin",
    "Intelligence folder",
    "Roler Submariner gold wrist watch",
    "Cardinal apartment key"
]
 
# initialize db (create tables)
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
                   seconds INTEGER NOT NULL
                   cost INTEGER NOT NULL
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS foundItems
                   (
                   raidID  INTEGER NOT NULL,
                   itemID   TEXT NOT NULL,
                   quantity INTEGER,

                   PRIMARY KEY(raidID, itemID),
                   FOREIGN KEY(raidID) REFERENCES raids(raidID)
                   FOREIGN KEY(itemID) REFERENCES items(itemID)
                   )
                   ''')
    
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS blackCard
                    (
                    cardID INTEGER PRIMARY KEY AUTOINCREMENT,
                    cost INTEGER NOT NULL
                    swipes INTEGER 
                    )
    ''')
    conn.commit()

# cycle trough trader price list to get therapists one
def api_getTherapistPrice(item):
    for trader in item["traderPrices"]:
        if trader["trader"]["name"] == "Therapist":
            return (trader["price"])

# compare flea price to therapist price
def api_getHighestPrice(item):
    therapistPrice = api_getTherapistPrice(item)
    fleaPrice = item["avg24hPrice"]
    if therapistPrice is None:
        return fleaPrice
    elif fleaPrice is None:
        return therapistPrice
    elif fleaPrice > therapistPrice:
        return fleaPrice
    else:
        return therapistPrice

# difference between 2 timestamps
def getTimeDelta(t1, t2):
    return abs(t1 - t2)

# check if 10 mins have passed
def getPassedTime():
    with open("timedelta.txt") as f:
        lastSaved = f.read()

    timeSinceLastSave = getTimeDelta(datetime.now(), datetime.fromisoformat(lastSaved))
    
    # check if 10 mins have passed since last API call
    if(timeSinceLastSave > timedelta(minutes=10)):
        with open("timedelta.txt", "w") as f:    
            f.write(datetime.now().isoformat())
        print("10 min cycle complete, calling API")
        return 1
    else:
        print("wait longer MAJ")
        return 0
    
# update the prices inside the DB
def updatePrices():
    if getPassedTime() == 0:
        return
    
    # call api 
    items = api.getItemData()

    # cycle trough the item list
    for name in trackedITEMS:
        item = items[name]

        # insert into db
        cursor.execute("INSERT INTO items (itemID, name, price) VALUES (?, ?, ?)", (item["id"], item["name"], api_getHighestPrice(item)))
    
    # test
    cursor.execute("SELECT * FROM items")

    print(cursor.fetchall())

# convert incoming raidTime string to integer Value
def getRaidTime(raidTime):
    # raidTime comes like this: 23:43, split the string into minutes and seconds
    minutes, seconds = raidTime.split(":")

    return (int(minutes) * 60) + int(seconds)

# add a new raid entry to the database
def addNewRaid(raidTime, foundItems, cost):
    # add raid stats
    cursor.execute("INSERT INTO raids (date, seconds, cost) VALUES (?, ?, ?)"), (datetime.now(), getRaidTime(raidTime), (cost / 5))

    currentRaid = cursor.lastrowid()
    # foundItems is a dict that has the item name and the number of times i found it as key:value pair
    for item in foundItems:
        itemID = item["id"]
        quantity = foundItems[item]
        cursor.execute("INSERT INTO foundItems (raidID, itemID, quantity) VALUES (?, ?, ?)"), (currentRaid, itemID, quantity)

# query SQL database for the Price
def getItemPrice(item):
    cursor.execute("SELECT price FROM items WHERE name = ?", (item))
    return cursor.fetchall()

# get all the raw money i made
def getMoneyEarned(rows):

    money = 0
    for name in rows:
        money += (getItemPrice(name) * rows[name][1])

    return money

def getStats():

    # dictionary for the stats
    stats = {
        "raidCounter":  0,
        "moneyEarned":  0,
        "moneySpent":   0,
        "itemsFound":  {},
        "revenue":  0
    }

    # find out how many raids are entried
    cursor.execute("SELECT COUNT(raidID) AS count FROM raids")
    stats["raidCounter"] = cursor.fetchall()

    # get all items found + quantity inside a 2d array
    cursor.execute("SELECT items.name AS itemName, foundItems.quantity AS quantity FROM foundItems INNER JOIN items ON items.itemID = foundItems.itemID WHERE foundItems.quantity != 0")

    allItems = cursor.fetchall()
    stats["moneyEarned"] = getMoneyEarned(allItems)

    cursor.execute("SELECT SUM(cost) FROM raids")

    moneySpent = cursor.fetchall()

    stats["itemsFound"] = allItems

    stats["revenue"] = stats["moneyEarned"] - stats["moneySpent"]

    return stats
import sqlite3
import api
from datetime import datetime
from datetime import timedelta

dbNAME = "tracker.db"
price = 900000

# list of tracked items
trackedITEMS = [
    "Physical Bitcoin",
    "Intelligence folder",
    "Roler Submariner gold wrist watch",
    "Cardinal apartment key",
    "TerraGroup Labs keycard (Blue)",
    "TerraGroup Labs keycard (Green)",
    "TerraGroup Labs keycard (Violet)",
    "TerraGroup Labs keycard (Yellow)",
    "TerraGroup Labs keycard (Black)",
    "TerraGroup Labs keycard (Red)"
]
 
# ===============
#      DB
# ==============

conn = sqlite3.connect(dbNAME)
cursor = conn.cursor()

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
                   seconds INTEGER NOT NULL,
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
                   FOREIGN KEY(raidID) REFERENCES raids(raidID),
                   FOREIGN KEY(itemID) REFERENCES items(itemID)
                   )
                   ''')
    
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS blackCard
                    (
                    cardID INTEGER PRIMARY KEY AUTOINCREMENT,
                    cost INTEGER NOT NULL,
                    swipes INTEGER 
                    )
                    ''')
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS netWorth (
                    entryID INTEGER PRIMARY KEY AUTOINCREMENT,
                    money INTEGER NOT NULL,
                    date TEXT NOT NULL
                    )
                    ''')
    conn.commit()

def getTotalRaids():
    if tupleToInt("SELECT MAX(raidID) FROM raids") == None:
        return 0
    else:
        return  tupleToInt("SELECT MAX(raidID) FROM raids")

# calculate the money made with the guaranteed spawns (intel, cardinal)
def getFixedProfit():
    return (getItemPrice("Cardinal apartment key") + getItemPrice("Intelligence folder")) * getTotalRaids()
    
def getKeycardName(color):
    return f"TerraGroup Labs keycard ({color})"

def addNetWorthEntry(money):
    cursor.execute("INSERT INTO netWorth (money, date) VALUES (?, ?)", (money, datetime.now()))
    conn.commit()

def getNetWorth():
    result = tupleToInt("SELECT money FROM netWorth ORDER BY entryID DESC LIMIT 1")
    return result

# query SQL database for the Price
def getItemPrice(item):
    cursor.execute("SELECT price FROM items WHERE name = ?", (item,))
    price = cursor.fetchone()

    return price[0] if price and price[0] is not None else 0

# get all the raw money i made
def getMoneyEarned(rows):
    money = 0

    for name, quantity in rows:
        price = getItemPrice(name)

        money += (price * quantity)

    return money

# convert incoming raidTime string to integer Value
def getRaidTime(raidTime):
    # raidTime comes like this: 23:43, split the string into minutes and seconds
    minutes, seconds = raidTime.split(":")

    return (int(minutes) * 60) + int(seconds)

# DB helper to turn weird ass data structures to a number
def tupleToInt(query):
    cursor.execute(query)
    tmp = cursor.fetchone()
    return tmp[0] if tmp is not None else 0

# ===============
#       API
# ==============

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
        return 1
        print("Please wait.... Updating Prices")
    else:
        return 0

# ==============
#      MAIN
# ==============

# add a new raid entry to the database (DB)
def addNewRaid(raidTime, foundItems, cost):
    # add raid stats
    cost = int(cost.replace(".", ""))
    cursor.execute("INSERT INTO raids (date, seconds, cost) VALUES (?, ?, ?)", (datetime.now(), getRaidTime(raidTime), (int(cost) / 5)))
    conn.commit()

    currentRaid = cursor.lastrowid
    # foundItems is a dict that has the item name and the number of times i found it as key:value pair
    for item in foundItems:
        cursor.execute("SELECT itemID FROM items WHERE name = ?", (item,))
        result = cursor.fetchone()

        if result:
            itemID = result[0]

        quantity = foundItems[item]
        cursor.execute("INSERT INTO foundItems (raidID, itemID, quantity) VALUES (?, ?, ?)", (currentRaid, itemID, quantity))
        conn.commit()

# update the prices inside the DB (API)
def updatePrices(mode):

    if mode != 1:
        if getPassedTime() == 0:
            return
    else:
        # call api 
        items = api.getItemData()

        # cycle trough the item list
        for name in trackedITEMS:
            item = items[name]

            # insert into db
            cursor.execute("INSERT INTO items (itemID, name, price) VALUES (?, ?, ?) ON CONFLICT(itemID) DO UPDATE SET price = excluded.price, name = excluded.name", (item["id"], item["name"], api_getHighestPrice(item)))
            conn.commit()


# get all the different statistics from the database
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
    stats["raidCounter"] = tupleToInt("SELECT COUNT(raidID) AS count FROM raids")

    # get all items found + quantity inside a 2d array
    cursor.execute("SELECT items.name AS itemName, foundItems.quantity AS quantity FROM foundItems INNER JOIN items ON items.itemID = foundItems.itemID WHERE foundItems.quantity != 0")

    allItems = cursor.fetchall()
    stats["moneyEarned"] = getMoneyEarned(allItems) + getFixedProfit()

    items = {}

    for name, quantity in allItems:
        if name in items:
            items[name] += quantity
        else:
            items[name] = quantity
    
    stats["itemsFound"] = items

    cursor.execute("SELECT SUM(cost) FROM raids")
    result_spent = cursor.fetchone()
    stats["moneySpent"] = result_spent[0] if result_spent and result_spent[0] is not None else 0

    # profit calculation
    stats["revenue"] = stats["moneyEarned"] - stats["moneySpent"]

    return stats

import sqlite3
import api as api
from datetime import datetime
from datetime import timedelta
import pandas as pd
import bcrypt

dbNAME = "../data/tracker.db"
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

# initialize db (create tables)
def initDB():
    with sqlite3.connect(dbNAME) as conn:
        cursor = conn.cursor()
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
                       cost INTEGER NOT NULL,
                       userID INTEGER,

                       FOREIGN KEY(userID) REFERENCES user(userID)
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
        # useless table for now, gonna leave it maybe make something with it later
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
                        date TEXT NOT NULL,
                        userID INTEGER,
                       
                       FOREIGN KEY(userID) REFERENCES user(userID)
                        )
                        ''')
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS user (
                       userID INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT,
                       password TEXT
                       )
                        ''')
        conn.commit()
    
def getKeycardName(color):
    return f"TerraGroup Labs keycard ({color})"

def addNetWorthEntry(money):
    with sqlite3.connect(dbNAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO netWorth (money, date) VALUES (?, ?)", (money, datetime.now()))
        conn.commit()

# convert incoming raidTime string to integer Value
def getRaidTime(raidTime):
    # raidTime comes like this: 23:43, split the string into minutes and seconds
    minutes, seconds = raidTime.split(":")

    return (int(minutes) * 60) + int(seconds)

# DB helper to turn weird ass data structures to a number
def tupleToInt(query):
    with sqlite3.connect(dbNAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        tmp = cursor.fetchone()
        return tmp[0] if tmp is not None else 0

# ===============
#       API
# ==============

def getFetchedItems():
    query = "SELECT COUNT(*) FROM items"
    
    with sqlite3.connect(dbNAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        count = cursor.fetchone()[0]
        return count

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
                
            print("Please wait.... Updating Prices")
        return 1
    else:
        return 0

# ==============
#      MAIN
# ==============

# add a new raid entry to the database (DB)
def addNewRaid(raidTime, foundItems, cost):
    # add raid stats
    cost = int(cost.replace(".", ""))
    with sqlite3.connect(dbNAME) as conn:
        cursor = conn.cursor()
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

    # if 1 is passed, timer will be skipped
    if mode != 1:
        if getPassedTime() == 0:
            return
        
    # call api 
    items = api.getItemData()

    # cycle trough the item list
    with sqlite3.connect(dbNAME) as conn:
        cursor = conn.cursor()
        for name, item in items.items():        
            if api_getHighestPrice(item) != None:
                if 10000 < api_getHighestPrice(item):
                    # insert into db
                    cursor.execute("INSERT INTO items (itemID, name, price) VALUES (?, ?, ?) ON CONFLICT(itemID) DO UPDATE SET price = excluded.price, name = excluded.name", (item["id"], item["name"], api_getHighestPrice(item)))
        conn.commit()
            
    # will return 0 if no error (will crash otherwise anyways lol)
    return items

# ============
# User Managment
# ============

def addNewUser(username, password):
    with sqlite3.connect(dbNAME) as conn:
        cursor = conn.cursor()

        cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password))
        conn.commit()

def createHash(password):
    bytes = password.encode('utf-8')

    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)

    return hash.decode('utf-8')

def checkPassword(username, password):
    users = df_getUserTable()

    enteredBytes = password.encode('utf-8')
    storedBytes = users[username]["password"]

    if bcrypt.checkpw(enteredBytes, storedBytes):
        return True
    else:
        return False 
# ============= 
# get Dataframes
# =============
def df_getItems():
       with sqlite3.connect(dbNAME) as conn:
        query = """
            SELECT 
                foundItems.raidID AS raidID,
                items.name AS itemName, 
                items.price AS price, 
                foundItems.quantity AS quantity 
            FROM foundItems 
            INNER JOIN items ON items.itemID = foundItems.itemID 
            WHERE foundItems.quantity > 0
        """
        return pd.read_sql_query(query, conn)

def df_getRaids():
    with sqlite3.connect(dbNAME) as conn:
        query = "SELECT raidID, date, seconds, cost from raids"
        return pd.read_sql_query(query, conn)
    
def df_getNetWorth():
    with sqlite3.connect(dbNAME) as conn:
        query = "SELECT money, date, entryID from netWorth"
        df = pd.read_sql_query(query, conn)
        return df.reset_index(drop=True)

def df_getItemsTable():
    with sqlite3.connect(dbNAME) as conn:
        query = "SELECT name, itemID, price from items"
        return pd.read_sql_query(query, conn)

def df_getUserTable():
    with sqlite3.connect(dbNAME) as conn:
        query = "SELECT userID, username, password from user"
        return pd.read_sql_query(query, conn)


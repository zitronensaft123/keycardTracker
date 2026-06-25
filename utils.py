# file to put all the calcualtions for the streamlit page, aswell as some html blocks so app,py stays clean

import matplotlib
import pandas as pd

import api
import db

def df_sumFoundItems():
    df = db.df_getItems()

    return df.groupby(["itemName", "price"], as_index=False)["quantity"].sum()

print(df_sumFoundItems())

# css string to remove annoying top bar
removeTopBar = """<style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
                </style>"""

# dict for the tarkovTracker stats
tarkovTrackerStats = {
    "account": {
        "name": "zitrone_3",
        "level": "38",
        "faction": "BEAR",
        "mode": "PVE",
    },
    "quests": {
        "kappa": "126",
        "lightkeeper": "84",
        "overall": "148" 
    },
    "traders": {
        "prapor": "3",
        "therapist": "4",
        "fence": "1",
        "skier": "4",
        "peacekeeper": "4",
        "mechanic": "3",
        "ragman": "3",
        "jaeger": "3",
        "lightkeeper": "3",
        "btr": "1"
    }
}


# ===========
# Calculations
#============

df_items = db.df_getItems()
df_raids = db.df_getRaids()
df_netWorth = db.df_getNetWorth()
df_foundItems = df_sumFoundItems()

def getStats():

    stats = {
        "keycard": {
            "moneySpent": 0,
            "moneyEarned": 0,
            "revenue": 0,
            "totalRaids": 0,
            "bestRaid": 0,
            "worstRaid": 0
        },
        "overall": {
            "currentMoney": 0,
            "maxMoney": 0,
            "minMoney": 0
        }
    }

    stats["keycard"]["moneySpent"] = df_raids["cost"].sum()
    stats["keycard"]["moneyEarned"] = (df_foundItems["price"] * df_foundItems["quantity"]).sum()
    stats["keycard"]["revenue"] = stats["keycard"]["moneyEarned"] - stats["keycard"]["moneySpent"]

    stats["keycard"]["totalRaids"] = len(df_raids)

    df_items["totalValue"] = df_items["price"] * df_items["quantity"]

    earnings = df_items.groupby("raidID")["totalValue"].sum()

    stats["keycard"]["bestRaid"] = earnings[earnings.idxmax()]
    stats["keycard"]["worstRaid"] = earnings[earnings.idxmin()]

    stats["overall"]["currentMoney"] = df_netWorth["money"].iloc[-1]
    stats["overall"]["maxMoney"] = df_netWorth["money"].max()
    stats["overall"]["minMoney"] = df_netWorth["money"].min()

    return stats
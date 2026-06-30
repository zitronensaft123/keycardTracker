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
def getTarkovTrackerStats():
    tarkovTrackerStats = {
        "account": {
            "name": "zitrone_3",
            "level": "42",
            "faction": "BEAR",
            "mode": "PVE",
        },
        "quests": {
            "kappa": "135",
            "lightkeeper": "100",
            "overall": "160" 
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

    return tarkovTrackerStats


# ===========
# Calculations
#============



def getStats():

    df_items = db.df_getItems()
    df_raids = db.df_getRaids()
    df_netWorth = db.df_getNetWorth()
    df_foundItems = df_sumFoundItems()
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
            "minMoney": 0,
            "previousMoney": 0
        }
    }

    if not df_raids.empty:
        stats["keycard"]["moneySpent"] = int(df_raids["cost"].sum())
        stats["keycard"]["totalRaids"] = len(df_raids)

    if not df_foundItems.empty:
        stats["keycard"]["moneyEarned"] = int((df_foundItems["price"] * df_foundItems["quantity"]).sum())
    
    stats["keycard"]["revenue"] = stats["keycard"]["moneyEarned"] - stats["keycard"]["moneySpent"]

    if not df_items.empty:
        df_items["totalValue"] = df_items["price"] * df_items["quantity"]
        earnings = df_items.groupby("raidID")["totalValue"].sum()
        if not earnings.empty:
            stats["keycard"]["bestRaid"] = int(earnings.max())
            stats["keycard"]["worstRaid"] = int(earnings.min())

    if not df_netWorth.empty:
        stats["overall"]["currentMoney"] = int(df_netWorth["money"].iloc[-1])
        if len(df_netWorth) > 1:
            stats["overall"]["previousMoney"] = int(df_netWorth["money"].iloc[-2])
        stats["overall"]["maxMoney"] = int(df_netWorth["money"].max())
        stats["overall"]["minMoney"] = int(df_netWorth["money"].min())

    return stats

def formatNumber(number, mode):
    # either add RUB or not
    if mode == 1:
        return f"{number:,} ₽".replace(",", ".")
    else:
        return f"{number:,}".replace(",", ".")

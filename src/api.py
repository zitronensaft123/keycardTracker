import requests
import datetime
from datetime import timedelta
import streamlit as st
import ssl
import json

#=============
# tarkov.dev
#=============

# call tarkov.dev for item info
def getItemData():

    query = """
    query {
        items(gameMode: pve) {
            id
            name
            avg24hPrice
            traderPrices {
                trader {
                    name
                }
                price
            }
            properties {
                ... on ItemPropertiesKey {
                    uses
                }
            }
        }
    }
"""

    headers = {"Content-Type": "application/json"}
    response = requests.post('https://api.tarkov.dev/graphql', headers=headers, json={'query': query})
    if response.status_code == 200:
        items = response.json()["data"]["items"]
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))

    # create lookup dic
    items_by_name = {
        item["name"]: item
        for item in items
    }

    return items_by_name

def getNeededItems():
    query = """
        query {
            items {
                name
                shortName
                usedInTasks {
                task {
                    name
                }
                count
                foundInRaid
                }
                usedInHideout {
                station {
                    name
                }
                level
                count
                }
            }
        }
    """

    headers = {"Content-Type": "application/json"}
    response = requests.post('https://api.tarkov.dev/graphql', headers=headers, json={'query': query})
    if response.status_code == 200:
        items = response.json()["data"]["items"]
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))

    neededItems = {
        "name": "",
        "hideout": 0,
        "fir_hideout": 0,
        "task": 0,
        "fir_task": 0,
        "total": 0
    }

    for item in items:
        hideout = sum(t["count"] for t in item["usedInHideout"] if not t["foundInRaid"])
        hideoutFiR = sum(t["count"] for t in item["usedInHideout"] if t["foundInRaid"])
        task = sum(t["count"] for t in item["usedInTask"] if not t["foundInRaid"])
        taskFiR = sum(t["count"] for t in item["usedInTask"] if not t["foundInRaid"])

        total = hideout + hideoutFiR + task + taskFiR

        if total > 0:
            neededItems["name"] = item["shortName"]
            neededItems["hideout"] = hideout
            neededItems["fir_hideout"] = hideoutFiR
            neededItems["task"] = task
            neededItems["fir_task"] = taskFiR
            neededItems["total"] = total

        print(neededItems)
        return neededItems

#===================
# tarkovtracker.org
# ==================

# ssl certificate errors, not even ai can fix it, will hardcode tarkovtracker stats for now maybe gonna try another time:

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


#===================
# tarkovtracker.org
# ==================

# ssl certificate errors, not even ai can fix it, will hardcode tarkovtracker stats for now maybe gonna try another time
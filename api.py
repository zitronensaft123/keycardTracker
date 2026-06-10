import requests

def getItemData():

    query = """
        query {
        items {
            id
            name
            avg24hPrice
            traderPrices {
            trader {
                name
            }
            price
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

    items_by_name = {
        item["name"]: item
        for item in items
    }

    return items_by_name
    
def getTherapistPrice(item):
    for trader in item["traderPrices"]:
        if trader["trader"]["name"] == "Therapist":
            return (trader["price"])

sigma = getItemData()
print(getTherapistPrice((sigma["Physical Bitcoin"])))

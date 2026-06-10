import requests

def queryBase(query):
    headers = {"Content-Type": "application/json"}
    response = requests.post('https://api.tarkov.dev/graphql', headers=headers, json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))


def queryItem(item):
    query = """
    {
        itemsByName(name: \"""" + item + """\") {
            id
            name
            avg24hPrice
            traderPrices {
                trader { name }
                price
            }
        }
    }
    """
    getData(queryBase(query))

def getData(data):
    # item id:
    itemID = data['data']['itemsByName'][0]['id']

    # name:
    name = data['data']['itemsByName'][0]['name']

    # price:
    price = 0
    
    traderPrice = (next(bit['price'] for bit in data['data']['itemsByName'][0]['traderPrices'] if bit['trader']['name'] == 'Therapist')) # brilliant oneliner
    fleaPrice = data['data']['itemsByName'][0]['avg24hPrice']
    if fleaPrice == None:
        price = traderPrice
    elif traderPrice > fleaPrice:
        price = traderPrice
    else:
        price = fleaPrice

queryItem("Physical Bitcoin")

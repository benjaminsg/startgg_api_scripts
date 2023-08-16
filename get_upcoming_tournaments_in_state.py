import requests
import config
from datetime import datetime

url = "https://api.start.gg/gql/alpha"

auth_token = config.auth_token

state = "WA"
perPage = 10

state = "\"" + state + "\""

query = """
            query {
                tournaments(query: {
                    perPage: %d
                    filter: {
                        countryCode: "US"
                        addrState: %s
                        past: false
                        upcoming: true
                        videogameIds: [
                            1
                        ]
                    }
                }) {
                    nodes {
                        id
                        name
                        city
                        addrState
                        startAt
                    }
                }
            }
    """ % (perPage, state)
    
obj = {"query": query}
    
response = requests.post(url=url,  headers={'Authorization': 'Bearer ' + auth_token}, json=obj)

if response.status_code == 200:
    tournaments = response.json()['data']['tournaments']['nodes']
    for tournament in tournaments:
        if(tournament['city'] == None):
            print(tournament['name'], ", " + tournament['addrState'])
        else:
            print(tournament['name'] + ", " + tournament['city'] + " " + tournament['addrState'])
        print(datetime.fromtimestamp(tournament['startAt']))
        print()
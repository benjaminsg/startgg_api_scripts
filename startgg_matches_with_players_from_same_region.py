import requests
import config

auth_token = config.auth_token

url = "https://api.start.gg/gql/alpha"

i = 1
sets_returned = 1

def get_event_id(slug):
    
    slug = "\"" + slug + "\""
    
    query = """
            query {
                tournament(slug: %s) {
                      events(limit: 20) {
                          id
                          name
                    }
                }
            }
            """ % slug
            
    obj = {"query": query}
    
    response = requests.post(url=url, headers={'Authorization': 'Bearer ' + auth_token}, json=obj)
    
    if response.status_code == 200:
        events = response.json()['data']['tournament']['events']
        for event in events:
            event_name = event['name']
            if "melee" in event_name.lower() and "singles" in event_name.lower():
                return event['id']
            
    return 0


event_id = get_event_id("apex-2022")


while(sets_returned > 0):
    query = """
        query {
            event(id: %d) {
              id
              name
              sets(
                  page: %d
                  perPage: 40
                  sortType: STANDARD
                  ) {
                      pageInfo {
                          total
                          }
                      nodes {
                          id
                          slots {
                              id
                              entrant {
                                  id
                                  name
                                  participants {
                                      user {
                                          location {
                                              state
                                              }
                                          }
                                      }
                                  }
                              standing {
                              placement
                                  stats {
                                      score {
                                          label
                                          value
                                          }
                                      }
                                  }
                              }
                          }
                      }
                }
            }
    """ % (event_id, i)
    
    obj = {"query": query}
    
    response = requests.post(url=url,  headers={'Authorization': 'Bearer ' + auth_token}, json=obj)
    
    NE_states = ['CT', 'MA', 'ME', 'NH', 'RI', 'VT']
    
    if response.status_code == 200:
        sets = response.json()['data']['event']['sets']['nodes']
        sets_returned = response.json()['data']['event']['sets']['pageInfo']['total']
        for set in sets:
            player1 = set['slots'][0]
            player2 = set['slots'][1]
            player1_score = player1['standing']['stats']['score']['value']
            player2_score = player2['standing']['stats']['score']['value']
            winner = player1 if (player1_score == 1) else player2
            player1_name = player1['entrant']['name']
            player2_name = player2['entrant']['name']
            player1_state = player1['entrant']['participants'][0]['user']['location']['state']
            player2_state = player2['entrant']['participants'][0]['user']['location']['state']
            if(player1_state in NE_states and player2_state in NE_states):
                if winner == player1:
                    print(player1_name + " (" + player1_state + ") "  + str(player1_score) + " - " + str(player2_score) + " " + player2_name + " (" + player2_state + ")")
                else:
                    print(player2_name + " (" + player2_state + ")  " + str(player2_score) + " - " + str(player1_score) + " " + player1_name + " (" + player1_state + ")")
    else:
        sets_returned = 0
    i += 1
        
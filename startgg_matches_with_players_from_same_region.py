import requests
import config
import logging
import time

auth_token = config.auth_token

url = "https://api.start.gg/gql/alpha"

sets_returned = 1
event_slug = "apex-2022"
region_name = "NEM"
write_to_txt = True

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


event_id = get_event_id(event_slug)

numRetries = 0
maxRetries = 10
txtAccess = False

if(write_to_txt):
    while not txtAccess:
    
        try:
            results = open("outputs/" + region_name + "_matches_at_" + event_slug + ".txt", "a")
    
            txtAccess = True
    
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            logging.exception(e)
            if numRetries > maxRetries:
                raise Exception("Exceeded maximum number of retries to access the file")
            print("Permission to access txt file denied, please close any programs with the file open")
            print("Waiting to retry write request to file")
            time.sleep(5)
            print("Retrying write request")
    
            numRetries += 1
    
            continue
    results.truncate(0)

players = set()
i = 1

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
    
    NE_states = {'CT', 'MA', 'ME', 'NH', 'RI', 'VT'}
    
    if response.status_code == 200:
        sets_played = response.json()['data']['event']['sets']['nodes']
        sets_returned = response.json()['data']['event']['sets']['pageInfo']['total']
        for set_played in sets_played:
            player1 = set_played['slots'][0]
            player2 = set_played['slots'][1]
            player1_score = player1['standing']['stats']['score']['value']
            player2_score = player2['standing']['stats']['score']['value']
            winner = player1 if (player1_score == 1) else player2
            player1_name = player1['entrant']['name']
            player2_name = player2['entrant']['name']
            player1_state = player1['entrant']['participants'][0]['user']['location']['state'] if player1['entrant']['participants'][0]['user']['location'] else ""
            player2_state = player2['entrant']['participants'][0]['user']['location']['state'] if player2['entrant']['participants'][0]['user']['location'] else ""
            if(player1_state in NE_states and player2_state in NE_states):
                players.add(player1_name)
                players.add(player2_name)
            
                if winner == player1:
                    print(player1_name + " (" + player1_state + ") "  + str(player1_score) + " - " + str(player2_score) + " " + player2_name + " (" + player2_state + ")")
                    if write_to_txt:
                        results.write(player1_name + " (" + player1_state + ") "  + str(player1_score) + " - " + str(player2_score) + " " + player2_name + " (" + player2_state + ")" + "\r\n")
                else:
                    print(player2_name + " (" + player2_state + ")  " + str(player2_score) + " - " + str(player1_score) + " " + player1_name + " (" + player1_state + ")")
                    if write_to_txt:
                        results.write(player2_name + " (" + player2_state + ")  " + str(player2_score) + " - " + str(player1_score) + " " + player1_name + " (" + player1_state + ")" + "\r\n")
    else:
        sets_returned = 0
        print(response)
        print(response.text)
    i += 1
print()
if write_to_txt:
    results.write("\r\n")
for player in players:
    print(player)
    if write_to_txt:
        results.write(player + "\r\n")
print()
print("done")
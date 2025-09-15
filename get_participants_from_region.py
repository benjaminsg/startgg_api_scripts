import requests
import config
import logging
import time

auth_token = config.auth_token

url = "https://api.start.gg/gql/alpha"

entrants_returned = 1
event_slug = "supernova-2025"
region_name = "WA"
write_to_txt = False

get_placements = False
get_socials = False

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
            if "melee" in event_name.lower() and "singles" in event_name.lower() and (not ("ladder" in event_name.lower())) and (not ("u18" in event_name.lower())):
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

placement_dict = {}
players = set()
players_without_user = set()
players_without_state = set()
i = 1

num_players = 0

while (entrants_returned > 0):
    query = """
        query {
          event(id: %d) {
            id
            name
            entrants(query: {
              page: %d
              perPage: 40
            }) {
              pageInfo {
              total
              totalPages
            }
            nodes {
              id
              participants {
                id
                gamerTag
                user {
                  location {
                    country
                    state
                  }
                  authorizations(types: TWITTER) {
                    externalUsername
                  }
                }
              }
              standing {
                placement
              }
            }
          }
        }
      }
    """ % (event_id, i)
    
    obj = {"query": query}
        
    response = requests.post(url=url,  headers={'Authorization': 'Bearer ' + auth_token}, json=obj)
        
    NE_states = {'CT', 'MA', 'ME', 'NH', 'RI', 'VT'}
        
    target_states = NE_states if region_name == "NE" else [region_name]
        
    if response.status_code == 200:
      entrants_processed = response.json()['data']['event']['entrants']['nodes']
      entrants_returned = response.json()['data']['event']['entrants']['pageInfo']['total']
      for entrant in entrants_processed:
          player = entrant['participants'][0]
          playerTag = player['gamerTag']
          if(player['user'] == None):
              state = ""
              players_without_user.add(playerTag)
          elif(player['user']['location'] == None):
            state = ""
            players_without_state.add(playerTag)
          else:
            state = player['user']['location']['state']
            if (state in target_states):
              if (get_placements):
                  placement = entrant['standing']['placement']
                  lastPlacementDigit = placement % 10
                  suffix = "th"
                  if(lastPlacementDigit == 1):
                      suffix = "st"
                  elif(lastPlacementDigit == 2):
                      suffix = "nd"
                  elif(lastPlacementDigit == 3):
                      if(not placement % 100 < 20):
                          suffix = "rd"
                  if(placement == 11 or placement == 12 or placement == 13):
                      suffix = "th"
                  placement_str = str(placement) + suffix
                  if(placement_str in placement_dict):
                      if(get_socials):
                          if(player['user']['authorizations'] != None):
                              placement_dict[placement_str] += (", " + playerTag + "(@" + player['user']['authorizations'][0]['externalUsername'] + ")")
                      else:
                        placement_dict[placement_str] += (", " + playerTag)
                  else:
                      if(get_socials):
                          if(player['user']['authorizations'] != None):
                              placement_dict[placement_str] = (playerTag + "(@" + player['user']['authorizations'][0]['externalUsername'] + ")")
                      else:  
                          placement_dict[placement_str] = playerTag
                  if(target_states == NE_states):
                      print(playerTag + " (" + state + "): " + str(placement) + suffix)
                  else:
                      print(playerTag)
                  num_players += 1
              else:
                  if(target_states == NE_states):
                      if(get_socials):
                          if(player['user']['authorizations'] != None):
                              print(playerTag + " (@" + player['user']['authorizations'][0]['externalUsername'] + ") [" + state + "]")
                          else:
                              print(playerTag)
                      else:
                        print(playerTag + " [" + state + "]")
                  else:
                      if(get_socials):
                          if(player['user']['authorizations'] != None):
                              print(playerTag + " (@" + player['user']['authorizations'][0]['externalUsername'] + ")")
                          else:
                              print(playerTag)
                      else:
                          print(playerTag)
                  players.add(playerTag)
                  num_players += 1
    else:
        sets_returned = 0
    i += 1
print()
if (get_placements):
  for key in placement_dict.keys():
    print(key)
    print(placement_dict[key])
    print()

print()

print(str(num_players) + " players")

print()

print("players without user")
for player in players_without_user:
    print(player)
print()

print("players without state")
for player in players_without_state:
    print(player)
print()

print("done")
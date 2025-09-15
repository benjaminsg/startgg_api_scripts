import requests
import config

auth_token = config.auth_token

url = "https://api.start.gg/gql/alpha"

def get_player_id(slug):
    
    slug = "\"" + slug + "\""
    
    query = """
            query {
                user(slug: %s) {
                    player {
                        id
                        gamerTag
                        }
                    name
                    }
                }
            """ % slug
            
    obj = {"query": query}
    
    response = requests.post(url=url, headers={'Authorization': 'Bearer ' + auth_token}, json=obj)
    
    if response.status_code == 200:
        id = response.json()['data']['user']['player']['id']
        return(id)

def get_sets(id, page, startEpoch):
    query = """
        query {
            player(id: %d) {
                id
                sets(perPage: 20, 
                     page: %d, 
                     filters: {
                         isEventOnline: false
                         updatedAfter: %d
                    }) {
                    nodes {
                        id
                        displayScore
                        event {
                            id
                            name
                            tournament {
                                id
                                name
                                }
                            startAt
                            videogame {
                                id
                                displayName
                                }
                            }
                        winnerId
                        slots {
                            id
                            entrant {
                                id
                                name
                                participants {
                                    id
                                        user {
                                            id
                                            player {
                                                id
                                                }
                                            }
                                        }
                                    }
                            }
                        }
                    }
                }
            }
    """ % (id, page, startEpoch)
    
    obj = {"query": query}
    
    response = requests.post(url=url, headers={'Authorization': 'Bearer ' + auth_token}, json=obj)
    
    if response.status_code == 200:
        sets = response.json()['data']['player']['sets']['nodes']
        return sets
    
def get_other_entrant(set, playerId):
    slots = set['slots']
    for i in range(len(slots)):
        entrant = slots[i]['entrant']
        user = entrant['participants'][0]['user']
        if user != None:
            player = user['player']
            if player != None:
                entrantId = player['id']
                if entrantId != playerId:
                    return entrant['name']
        else:
            j = 1 - i
            if slots[j]['entrant']['participants'][0]['user'] != None:
                return entrant['name']
    return None

def get_player_entrant_id(set, playerId):
    slots = set['slots']
    for slot in slots:
        entrant = slot['entrant']
        user = entrant['participants'][0]['user']
        if user != None:
            player = user['player']
            if player != None:
                entrantId = player['id']
                if entrantId == playerId:
                    return entrant['id']
    return None

def get_string_after_char(main_string, character):
    if main_string == None:
        return ""
    if '|' in main_string:
        index = main_string.find(character)
        if index != -1:
            return main_string[index + len(character) + 1:]
        else:
            return ""
    return main_string

playerId = get_player_id("1419963f")
i = 1
startEpoch = 1735718400
endEpoch = 1756710000
wins = {}
losses = {}
while True:
    sets = get_sets(playerId, i, startEpoch)
    if len(sets) < 1:
        break
    for set in sets:
        eventStart = set['event']['startAt']
        eventName = set['event']['name'].lower()
        eventGameId = set['event']['videogame']['id']
        winnerId = set['winnerId']
        if (eventStart <= endEpoch and eventGameId == 1 and 'singles' in eventName and not ('amateur' in eventName)):
            otherEntrantFullTag = get_other_entrant(set, playerId)
            otherEntrantTag = get_string_after_char(otherEntrantFullTag, '|')
            tournament = set['event']['tournament']['name']
            if winnerId == get_player_entrant_id(set, playerId):
                if otherEntrantTag in wins:
                    wins[otherEntrantTag].append(tournament)
                else:
                    wins[otherEntrantTag] = [tournament]
            else:
                if otherEntrantTag in losses:
                    losses[otherEntrantTag].append(tournament)
                else:
                    losses[otherEntrantTag] = [tournament]
    i += 1
print("wins")    
print(wins)
print("losses")
print(losses)
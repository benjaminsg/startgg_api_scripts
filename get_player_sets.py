import requests
import config
import locals
import monthlies
import regionals_and_majors
import player_rank
from itertools import zip_longest

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
        if (entrant != None):
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

def add_win_or_loss(set, tournament, playerId, wins, losses, otherEntrantTag):
    if (set['displayScore'] != 'DQ'):
        if winnerId == get_player_entrant_id(set, playerId):
            wins.append(otherEntrantTag)
        else:
            losses.append(otherEntrantTag)

def get_player_rank(player_ranks, player):
    return player_ranks[player] if player in player_ranks else ''

def get_player_priority(player, player_ranks, priority_mapping):
    if (player in player_ranks):
        return priority_mapping[player_ranks[player]]
    else:
        return 100

# Hufff 1419963f
playerId = get_player_id("3352d0d8")
i = 1
startEpoch = 1745121600
endEpoch = 1760846340
local_wins = []
local_losses = []
monthly_wins = []
monthly_losses = []
regional_and_major_wins = []
regional_and_major_losses = []

excluded_tournaments = [
    'MMOM 2022',
    'A Secret Deli Birthday Bash',
    'Front Runners #27',
    'Mork Fest',
    'SCONEFEST Summer 2025 #1',
    'SCONEFEST Fall 2025 #4: The REAL Quebecup Prelocal',
    'SSS 20.3 - A New Hampshire Melee Monthly!',
    'Final Warning: The Golden Age - Chapter III',
    'Giga HoG 7.1',
    'SSS 20.4 - A New Hampshire Melee Monthly!',
    'The 3rd New England Melee Spartan',
    'Allston Allstars III'
    ]

local_events = locals.locals.splitlines()
monthly_events = monthlies.monthlies.splitlines()
regional_and_major_events = regionals_and_majors.regionals_and_majors.splitlines()

other_events = set()

max_tag_len = 0

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
            if ('|' in otherEntrantTag):
                otherEntrantTag = get_string_after_char(otherEntrantTag, '|')
            tournament = set['event']['tournament']['name']
            if (not tournament in excluded_tournaments):
                if len(otherEntrantTag) > max_tag_len:
                    max_tag_len = len(otherEntrantTag)
                if (tournament in local_events):
                    add_win_or_loss(set, tournament, playerId, local_wins, local_losses, otherEntrantTag)
                elif (tournament in monthly_events):
                    add_win_or_loss(set, tournament, playerId, monthly_wins, monthly_losses, otherEntrantTag)
                elif (tournament in regional_and_major_events):
                    add_win_or_loss(set, tournament, playerId, regional_and_major_wins, regional_and_major_losses, otherEntrantTag)
                else:
                    other_events.add(tournament)
    i += 1
print("\twins")
print()
player_ranks = player_rank.player_rank
priority_mapping = player_rank.priority_mapping
local_wins = sorted(local_wins, key=str.lower)
local_wins = sorted(local_wins, key=lambda player: get_player_priority(player, player_ranks, priority_mapping))
monthly_wins = sorted(monthly_wins, key=str.lower)
monthly_wins = sorted(monthly_wins, key=lambda player: get_player_priority(player, player_ranks, priority_mapping))
regional_and_major_wins = sorted(regional_and_major_wins, key=str.lower)
regional_and_major_wins = sorted(regional_and_major_wins, key=lambda player: get_player_priority(player, player_ranks, priority_mapping))
col_len = max_tag_len + 10
final_col_len = max_tag_len + 5
for local_win, monthly_win, regional_or_major_win in zip_longest(local_wins, monthly_wins, regional_and_major_wins, fillvalue=''):
    local_win_rank = get_player_rank(player_ranks, local_win)
    monthly_win_rank = get_player_rank(player_ranks, monthly_win)
    regional_or_major_win_rank = get_player_rank(player_ranks, regional_or_major_win)
    print(local_win_rank + '\t' + local_win + '\t' + monthly_win_rank + '\t' + monthly_win + '\t' + regional_or_major_win_rank + '\t' + regional_or_major_win)
print()
print("\tlosses")
print()
local_losses = sorted(local_losses, key=str.lower)
local_losses = sorted(local_losses, key=lambda player: get_player_priority(player, player_ranks, priority_mapping))
monthly_losses = sorted(monthly_losses, key=str.lower)
monthly_losses = sorted(monthly_losses, key=lambda player: get_player_priority(player, player_ranks, priority_mapping))
regional_and_major_losses = sorted(regional_and_major_losses, key=str.lower)
regional_and_major_losses = sorted(regional_and_major_losses, key=lambda player: get_player_priority(player, player_ranks, priority_mapping))
for local_loss, monthly_loss, regional_or_major_loss in zip_longest(local_losses, monthly_losses, regional_and_major_losses, fillvalue=''):
    local_loss_rank = get_player_rank(player_ranks, local_loss)
    monthly_loss_rank = get_player_rank(player_ranks, monthly_loss)
    regional_or_major_loss_rank = get_player_rank(player_ranks, regional_or_major_loss)
    print(local_loss_rank + '\t' + local_loss + '\t' + monthly_loss_rank + '\t' + monthly_loss + '\t' + regional_or_major_loss_rank + '\t' + regional_or_major_loss)
print()
print("other events")
print(other_events)
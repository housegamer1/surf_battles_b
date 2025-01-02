import requests
import json
import time
import datetime

######################
# Team related stuff #
######################
class Team:
    name    = None
    players = []

    def __init__(self, name, players) -> None:
        self.name = name
        self.players = players

    def add_player(self, player):
        if player not in self.players:
            self.players.append(player)

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)

    def get_name(self):
        return self.name

    def get_players(self):
        return self.players


#######################
# Match related stuff #
#######################
class Match:
    id              = None
    starttime       = None
    duration        = None
    teams           = []
    surfmap         = None
    zone            = None
    leaderboard     = None
    valid           = True

    def __init__(self, starttime, duration, surfmap, zone, teams) -> None:
        self.starttime = starttime
        self.duration = duration #in minutes i guess. not sure if we even need this in the backend, since frontend likely tracks time
        self.surfmap = surfmap
        self.zone = zone
        self.teams = teams

        idstring = ""
        teamsize = 0
        for team in self.teams:
            players = team.get_players()
            playercount = len(players)

            if teamsize == 0:
                teamsize = playercount
            elif teamsize != playercount:
                self.valid = False



            for player in team.get_players():
                idstring = idstring + str(player.get_id()) + "_"

            if not self.valid:
                idstring = "INVALID_UNEQUAL_SIZE_TEAMS_" + idstring

        self.id = idstring + str(self.starttime.timestamp())

    def get_id(self):
        return self.id
    
    def get_starttime(self):
        return self.starttime
    
    def get_duration(self):
        return self.duration
    
    def get_teams(self):
        return self.teams
    
    def get_surfmap(self):
        return self.surfmap
    
    def get_zone(self):
        return self.zone
    
    def get_leaderboard(self):
        return self.leaderboard
    
    def get_valid(self):
        return self.valid
    
    def determine_leading_team(self):
        team_times = [] #trying to make it so that in theory more than 2 teams could compete in a match
        times_only = []
        has_identical_times = False

        for team in self.teams:
            team_sum = 0
            players_set_times = 0

            for player in team.get_players():
                pb = player.get_personal_best(self.surfmap, self.zone)

                if pb != None:
                    team_sum = team_sum + pb
                    players_set_times = players_set_times + 1

            teamdict = { #TODO expand leaderboard objects to contain the times set by the players
                "team": team,
                "times_set": players_set_times,
                "sum_time": team_sum
            }

            if team_sum > 0:
                if team_sum not in times_only:
                    times_only.append(team_sum)
                else:
                    has_identical_times = True

            team_times.append(teamdict.copy())

        sorted_by_time = sorted(team_times, key=lambda item : (item["sum_time"]))
        sorted_by_completions = sorted(sorted_by_time, key=lambda item : (item["times_set"]), reverse=True) # should be sorted by highest amount of completions with lowest time
        
        self.leaderboard = {
            "leading_team" : sorted_by_completions[0]["team"].get_name(),
            "entries": sorted_by_completions
        }

        if len(self.leaderboard["entries"]) > 1 and has_identical_times:
            leaderdict = None
            identical_teams = []

            for entry in self.leaderboard["entries"]:
                if leaderdict == None:
                    leaderdict = entry.copy()
                    identical_teams.append(leaderdict["team"].get_name()) #add leading team to check if anyone tied them. this means tie check is only effective for the lead though..
                    continue

                if entry["sum_time"] == leaderdict["sum_time"] and entry["times_set"] == leaderdict["times_set"]:
                    identical_teams.append(entry["team"].get_name())

            if len(identical_teams) > 1:
                self.leaderboard["leading_team"]  = "It's a draw! Between " + ", ".join(identical_teams)




########################
# Player related stuff #
########################
class Record:
    time        = None
    timestamp   = None
    map         = None
    zone        = None

    def __init__(self, time, timestamp, map , zone) -> None:
        self.time = time
        self.timestamp = timestamp
        self.map = map
        self.zone = zone

    def get_time(self):
        return self.time
    
    def get_timestamp(self):
        return self.timestamp
    
    def get_map(self):
        return self.map
    
    def get_zone(self):
        return self.zone


class Player:
    id      = None
    name    = None
    records = None
    server  = 0

    def __init__(self, id) -> None:
        self.id = id
        self.name = request_name(self.id)
        self.records = []

    def add_time(self, settime, settimestamp, map, zone):
        global launchtime
        
        if isinstance(settimestamp, datetime.datetime):
            finishstamp = settimestamp
        else:
            finishstamp = datetime.datetime.strptime(settimestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

        #prevent records from before program launch being recorded
        if finishstamp > launchtime:

            finish = Record(settime, settimestamp, map, zone)

            for entry in self.records:
                if entry.get_timestamp() == settimestamp:
                    return #time set at this timestamp already exists, skip.

            self.records.append(finish)

    def clear_times(self):
        self.records.clear()

    def tostring(self):
        return str(self.name) + "    " + str(self.id)
    
    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name

    def get_records(self):
        return self.records
    
    def get_personal_best(self, surfmap, zone):
        fastest_time = None
        for record in self.records:
            if record.get_map() == surfmap and record.get_zone() == zone:
                time = record.get_time()

                if fastest_time == None or time < fastest_time:
                    fastest_time = time
                
        return fastest_time
    
    def get_server_number(self):
        return self.server

#############
# API Calls #
#############

def request_name(id):
    endpoint = shapi + "playerinfo/" + str(id)
    content = request(endpoint, 200)

    if content != None and len(content) == 1: #Endpoint returns [{}] for a single player
        content = content[0]

        if "name" in content:
            return content["name"]
        
    return "N/A"


def check_results():
    now = time.time()
    global lastResultCheck
    global cfg
    global lastPollResult

    if lastResultCheck == None or now - lastResultCheck > 2: #allow each new api request only after 2 seconds
        lastResultCheck = now
            
        #TODO with every refresh cycle, go through all players in the matches and see if they are connected and if that server is running the right map
        #using general api and filtering here to reduce api calls
        endpoint = shapi + "finishes"
        content = request(endpoint, 201)

        if content != None and (lastPollResult == None or lastPollResult != content):
            for entry in content:
                
                if cfg.surfmap != None:
                    if entry["map"] != cfg.surfmap:
                        continue

                if cfg.zone != None:
                    if str(entry["track"]) != cfg.zone:
                        continue

                for player in cfg.players:
                    if entry["steamid"] == player.get_id():
                        #print("adding time " + str(entry["time"]) + " for player " + player.get_name() + "with steamid " + entry["steamid"] + "for player id " + str(player.get_id()) + " on map " + entry["map"] + " and track " + str(entry["track"]))
                        player.add_time(entry["time"], entry["date"], entry["map"], entry["track"])

            lastPollResult = content


def request(url, acceptCode):
    try:
        result = requests.get(url)
        #print("Request: " + url + " [" + str(result.status_code) + "]")
        if result.status_code == acceptCode:
            content = result.content.decode("utf-8")
            return json.loads(content)

        return None
                   
    except requests.exceptions.RequestException as e:
        print("Caught error: " + str(e))
        return None


##################################
# json stuff yoinked from da web #
##################################
def get_json(obj):
    return json.loads(
        json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
    )


#######################
# globals because idc #
#######################
shapi = "https://api.surfheaven.eu/api/"
lastConfigReload = None
lastResultCheck = None
lastPollResult = None
launchtime = datetime.datetime.now(datetime.timezone.utc)#.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

###########
# Main :) #
###########
def main():

    while True:        
        #Periodically check api for new results
        check_results()

        #reduce cpu load. response time should be good enough idc
        time.sleep(0.1)
    
    
if __name__ == "__main__":
    main()
import requests
import json
import time
import datetime
import threading
import dateutil
import uuid

######################
# Team related stuff #
######################
class Team:
    name    = None
    players = []
    diff_to_fastest_team = None

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

    def set_diff_to_fastest_team(self, diff):
        self.diff_to_fastest_team = trunc_to_tick(diff)

    def get_diff_to_fastest_team(self):
        return self.diff_to_fastest_team

    def sort_players_by_pb(self):
        self.players = sorted(self.players, key=lambda item : (item.get_diff_to_fastest_player()))


#######################
# Match related stuff #
#######################
class Match:
    id                  = None
    starttime           = None
    duration            = None
    teams               = []
    surfmap             = None
    zone                = None
    leaderboard         = None
    valid               = True #setting the value here instead of init makes it not appear when returning a match via the api
    match_over          = None


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

            idstring = str(uuid.uuid4())
            if not self.valid:
                idstring = "INVALID_UNEQUAL_SIZE_TEAMS_" + idstring

        self.id =idstring
        self.match_over = False
        global matches
        matches.append(self)

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

    def get_match_over(self):
        return self.match_over

    def is_still_running(self):
        if self.match_over:
            return False

        now = datetime.datetime.now(datetime.timezone.utc)
        duration_as_delta = datetime.timedelta(minutes=self.duration)
        if now - self.starttime >= duration_as_delta:
            self.match_over = True
            return False
        return True

    def determine_leading_team(self):
        team_times = [] #trying to make it so that in theory more than 2 teams could compete in a match
        times_only = []
        has_identical_times = False

        for team in self.teams:
            team_sum = 0
            players_set_times = 0

            for player in team.get_players():
                pb = player.get_personal_best(self.surfmap, self.zone)

                if pb != "No time on match map yet":
                    team_sum = team_sum + pb
                    players_set_times = players_set_times + 1

            teamdict = {
                "team": team,
                "times_set": players_set_times,
                "sum_time": team_sum
            }


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
                self.leaderboard["leading_team"]  = "It's a draw! Between " + " and ".join(identical_teams)

    def determine_team_delta(self):
        if self.leaderboard != None:
            leading_time = None

            for team in self.leaderboard["entries"]:
                team_time = team["sum_time"]
    
                if leading_time == None:
                    leading_time = team_time

                team["team"].set_diff_to_fastest_team(team_time - leading_time)

    def determine_player_delta(self):
        if self.leaderboard != None:
            players = []
            leading_time = None

            for team in self.leaderboard["entries"]:
                teamobj = team["team"]
                team_players = teamobj.get_players()

                for player in team_players:
                    pb = player.get_personal_best(self.surfmap, self.zone)
                    if pb != "No time on match map yet":
                        players.append({"player":player, "time":pb})

            sorted_by_time = sorted(players, key=lambda item : (item["time"]))


            for player in sorted_by_time:
                pb = player["time"]

                if leading_time == None:
                    leading_time = pb

                player["player"].set_diff_to_fastest_player(pb - leading_time)

        for team in self.teams:
            #this needs the diff to fastest player to be set
            team.sort_players_by_pb()


########################
# Player related stuff #
########################
class Record:
    time        = None
    timestamp   = None
    map         = None
    zone        = None
    ispr        = None
    iswr        = None
    rank        = None

    def __init__(self, time, timestamp, map , zone, ispr, iswr, rank) -> None:
        self.time = time
        self.timestamp = timestamp
        self.map = map
        self.zone = zone
        self.ispr = ispr
        self.iswr = iswr
        self.rank = rank

    def get_time(self):
        return self.time

    def get_timestamp(self):
        return self.timestamp

    def get_map(self):
        return self.map

    def get_zone(self):
        return self.zone

    def get_ispr(self):
        return self.ispr

    def get_iswr(self):
        return self.iswr

    def get_rank(self):
        return self.rank


class Player:
    id      = None
    name    = None
    records = None
    diff_to_fastest_player = 999999 #setting the value here instead of init makes it not appear when returning a match via the api
    connected = None
    fastest_time = None

    def __init__(self, id) -> None:
        self.id = id
        self.name = request_name(self.id)
        self.records = []
        self.connected = "Offline"
        self.fastest_time = "No time on match map yet"

    def add_time(self, settime, settimestamp, map, zone, starttime, ispr, iswr, rank):

        if isinstance(settimestamp, datetime.datetime):
            finishstamp = settimestamp
        else:
            finishstamp = dateutil.parser.parse(settimestamp)

        #prevent records from before program launch being recorded
        if finishstamp >= starttime:

            finish = Record(settime, settimestamp, map, zone, ispr, iswr, rank)

            for entry in self.records:
                if entry.get_timestamp() == settimestamp:
                    return #time set at this timestamp already exists, skip.

            self.records.append(finish)
            self.records = sorted(self.records, key=lambda item : (item.get_time()))

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
        fastest_time = self.fastest_time
        for record in self.records:
            if record.get_map() == surfmap and record.get_zone() == zone:
                time = record.get_time()

                if fastest_time == "No time on match map yet" or time < fastest_time:
                    fastest_time = time
        self.fastest_time = fastest_time
        return fastest_time

    def set_diff_to_fastest_player(self, diff):
        self.diff_to_fastest_player = trunc_to_tick(diff)

    def get_diff_to_fastest_player(self):
        return self.diff_to_fastest_player

    def determine_connected(self, online, surfmap):
    #this function doesnt request by itself. requesting for every player would be overkill. instead it takes the result out of the main loop so we request only ever 2 sec.
        for connectedplayer in online:
            if connectedplayer["steamid"] == self.get_id():
                if connectedplayer["map"] == surfmap:
                    self.connected = "Online"
                    return
                else:
                    self.connected = "Online, wrong map"
                    return

        self.connected = "Offline"


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

def request(url, acceptCode=200):
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


###################
# ghetto truncing #
###################
def trunc_to_tick(number):
    return float(str(number)[:5])

#######################
# globals because idc #
#######################
shapi = "https://api.surfheaven.eu/api/"
lastResultCheck = None
lastPollResult = None
launchtime = datetime.datetime.now(datetime.timezone.utc)#.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
matches = []
threadcontrol = threading.Event()




#############
# main loop #
#############
def backend_loop():
    while not threadcontrol.is_set():
        global lastPollResult
        #using general api and filtering here to reduce api calls
        endpoint = shapi + "finishes"
        content = request(endpoint, 201)
        online = request(shapi + "online")
        #print(".", end="", flush=True)


        for match in matches:
            if match.is_still_running():
                for entry in content:

                    #if match.get_surfmap() != None:
                    #    if entry["map"] != match.get_surfmap():
                    #        continue

                    #if match.get_zone() != None:
                    #    if entry["track"] != match.get_zone():
                    #        continue

                    for team in match.get_teams():
                        for player in team.get_players():
                            player.determine_connected(online, match.get_surfmap())
                            if content != None and (lastPollResult == None or lastPollResult != content):
                                if entry["steamid"] == str(player.get_id()):
                                    #print("adding time " + str(entry["time"]) + " for player " + player.get_name() + "with steamid " + entry["steamid"] + "for player id " + str(player.get_id()) + " on map " + entry["map"] + " and track " + str(entry["track"]))
                                    player.add_time(entry["time"], entry["date"], entry["map"], entry["track"], match.get_starttime(), entry["ispr"], entry["iswr"], entry["rank"])

                    match.determine_leading_team()
                    match.determine_team_delta()
                    match.determine_player_delta()

        lastPollResult = content
        time.sleep(2)
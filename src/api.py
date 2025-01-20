from flask import Blueprint, request
import src.backend as backend
import datetime
import json

api_routes = Blueprint("api_routes", __name__)

@api_routes.route("/")
def hello_world():
    return "Nothing to see here."


@api_routes.route("/matches")
def matches():
    return backend.get_json(backend.matches)

@api_routes.route("/match/<matchid>")
def match(matchid):
    for match in backend.matches:
        if match.get_id() == matchid:
            return backend.get_json(match)

    return "Match ID not found"

@api_routes.route("/addmatch", methods=["POST"])
def addmatch():
    if request.content_type == "application/json":
        rq_json = request.json
        if isinstance(rq_json, dict):
            data = rq_json
        else:
            data = json.loads(rq_json)

        if validate_request_data(data):
            return prepare_new_match(data)
        else:
            return "post request missing essential data"

    else:
        return "Invalid content type. Please use application/json"




#functions to prepare requests for the backend

def validate_zone_exists(map, zone):

    if isinstance(zone,str) and zone.isdecimal():
        zone = int(zone)

    result = backend.request(backend.shapi + "maps")
    for entry in result:
        if entry["map"] == map and entry["bonus"] >= zone:
            return True
    return False



def validate_request_data(data):
    has_map = "map" in data
    has_zone = "zone" in data
    zone_exists = has_map and has_zone and validate_zone_exists(data["map"], data["zone"])

    has_teams = "teams" in data and isinstance(data["teams"], list) and len(data["teams"]) > 1
    teamcount = 0
    teams_with_players = 0
    
    if has_map and has_zone and has_teams:    
        for team in data["teams"]:
            teamcount = teamcount + 1
            if "players" in team and len(team["players"]) > 0:
                teams_with_players = teams_with_players + 1
            
    return zone_exists and has_teams and teamcount != 0 and (teams_with_players == teamcount)

def prepare_new_match(data):
    surfmap = data["map"]
    zone = data["zone"]
    teams = []

    for team in data["teams"]:
        teamname = team["name"]
        players = []
        for player in team["players"]:
            players.append(backend.Player(player))

        teams.append(backend.Team(teamname, players))

    starttime = datetime.datetime.now(datetime.timezone.utc)
    duration = 10 #duration is irrelevant for the backend at this point....
    match = backend.Match(starttime, duration, surfmap, zone, teams)
    return "created match: " + match.get_id()


#routes only for internal testing
@api_routes.route("/testing_settimes")
def testing_settimes():
    now = datetime.datetime.now(datetime.timezone.utc)
    match = backend.matches[0]
    time = 10
    for team in match.get_teams():
        time = time +1
        for player in team.get_players():
            player.add_time(time, now, "surf_njv", 4)

    match.determine_leading_team()
    match.determine_team_delta()
    match.determine_player_delta()
    return "Times set."

@api_routes.route("/testing_newmatch")
def testing_newmatch():
    player1_id = 38142345
    player2_id = 58229111
    player1 = backend.Player(player1_id)
    player2 = backend.Player(player2_id)
    team1 = backend.Team("A", [player1])
    team2 = backend.Team("B", [player2])


    starttime = datetime.datetime.now(datetime.timezone.utc)
    duration = 10 #minutes

    teams_match1 = [team1, team2]

    surfmap_match1 = "surf_njv"
    zone_match1 = 4

    backend.Match(starttime, duration, surfmap_match1, zone_match1, teams_match1)
    return "New match created!"


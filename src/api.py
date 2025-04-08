from flask import Blueprint, request, jsonify
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

    data = {"message": "Match ID not found"}
    return jsonify(data), 404

@api_routes.route("/addmatch", methods=["POST"])
def addmatch():
    if request.content_type == "application/json":
        rq_json = request.json
        if isinstance(rq_json, dict):
            data = rq_json
        else:
            data = json.loads(rq_json)

        if validate_add_request(data):
            return prepare_new_match(data), 201
        else:
            data = {"message": "post request missing essential data"}
            return jsonify(data), 400
    else:
        data = {"message": "Invalid content type. Please use application/json"}
        return jsonify(data), 406

@api_routes.route("/controlmatch", methods=["POST"])
def controlmatch():
    if request.content_type == "application/json":
        rq_json = request.json
        if isinstance(rq_json, dict):
            data = rq_json
        else:
            data = json.loads(rq_json)

        if "id" in data and "set_status" in data:
            id = data["id"]
            newstatus = data["set_status"]

            found_match = backend.get_match(id)
            if found_match != None:
                data = {"message": "New match status is " + newstatus, "id": id}
                if newstatus == "NOT_STARTED":
                    found_match.set_match_status(backend.MatchStatus.NOT_STARTED)
                    return jsonify(data), 200
                elif newstatus == "RUNNING":
                    found_match.set_match_status(backend.MatchStatus.RUNNING)
                    return jsonify(data), 200
                elif newstatus == "PAUSED":
                    found_match.set_match_status(backend.MatchStatus.PAUSED)
                    return jsonify(data), 200
                elif newstatus == "OVER":
                    found_match.set_match_status(backend.MatchStatus.OVER)
                    return jsonify(data), 200
                else:
                    data = {"message": "Invalid match status " + newstatus + " to set. Can only set NOT_STARTED, RUNNING, PAUSED, OVER", "id": id}
                    return jsonify(data), 400
            else:
                data = {"message": "Match id not found", "id" : id}
                return jsonify(data), 404
        else:
            data = {"message": "Request missing essential data, please provide id and set_status"}
            return jsonify(data), 400
    else:
        data = {"message": "Invalid content type. Please use application/json"}
        return jsonify(data), 406


@api_routes.route("/removematch", methods=["DELETE"])
def removematch():
    if request.content_type == "application/json":
        rq_json = request.json
        if isinstance(rq_json, dict):
            data = rq_json
        else:
            data = json.loads(rq_json)

        if validate_remove_request(data):
            id = data["id"]
            found_match = backend.get_match(id)

            #i dont want to modify the list while i loop over it. surely it would be fine but lets just not.
            if found_match != None:
                backend.matches.remove(found_match)
                data = {"message": "Deleted match", "id": id}
                return jsonify(data), 200
            else:
                data = {"message": "Match not deleted. Could not find match id", "id": id}
                return jsonify(data), 404
        else:
            data = {"message": "post request missing essential data"}
            return jsonify(data), 400
    else:
        data = {"message": "Invalid content type. Please use application/json"}
        return jsonify(data), 406



#functions to prepare requests for the backend
def validate_zone_exists(map, zone):
    if isinstance(zone,str) and zone.isdecimal():
        zone = int(zone)

    result = backend.request(backend.shapi + "maps")
    for entry in result:
        if entry["map"] == map and entry["bonus"] >= zone:
            return True
    return False

def validate_add_request(data):
    has_map = "map" in data
    has_zone = "zone" in data
    zone_exists = has_map and has_zone and validate_zone_exists(data["map"], data["zone"])

    has_teams = "teams" in data and isinstance(data["teams"], list) and len(data["teams"]) > 1
    teamcount = 0
    teams_with_players = 0
    teams_with_name = 0

    has_duration = "duration" in data

    if has_map and has_zone and has_teams:
        for team in data["teams"]:
            teamcount = teamcount + 1
            if "players" in team and len(team["players"]) > 0:
                teams_with_players = teams_with_players + 1
            if "name" in team and team["name"] != "":
                teams_with_name = teams_with_name + 1

    return zone_exists and has_teams and teamcount != 0 and (teams_with_players == teamcount) and (teams_with_name == teamcount) and has_duration

def validate_remove_request(data):
    #so far only check id. not sure if we need to check more in the future
    if "id" in data:
        return True

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
    duration = data["duration"]
    match = backend.Match(starttime, duration, surfmap, zone, teams)
    data = {"message": "created match", "id": match.get_id()}
    return jsonify(data)


#routes only for internal testing
# @api_routes.route("/testing_settimes")
# def testing_settimes():
#     now = datetime.datetime.now(datetime.timezone.utc)
#     match = backend.matches[0]
#     time = 10
#     for team in match.get_teams():
#         time = time +1
#         for player in team.get_players():
#             player.add_time(time, now, "surf_njv", 4, now, 0, 0, 0)

#     match.determine_leading_team()
#     match.determine_team_delta()
#     match.determine_player_delta()
#     return "Times set."

# @api_routes.route("/testing_newmatch")
# def testing_newmatch():
#     player1_id = 38142345
#     player2_id = 58229111
#     player1 = backend.Player(player1_id)
#     player2 = backend.Player(player2_id)
#     team1 = backend.Team("A", [player1])
#     team2 = backend.Team("B", [player2])


#     starttime = datetime.datetime.now(datetime.timezone.utc)
#     duration = 10 #minutes

#     teams_match1 = [team1, team2]

#     surfmap_match1 = "surf_njv"
#     zone_match1 = 4

#     backend.Match(starttime, duration, surfmap_match1, zone_match1, teams_match1)
#     return "New match created!"


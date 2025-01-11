from flask import Flask, request
import backend
import threading
import datetime

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Nothing to see here."

@app.route("/matches")
def matches():
    return backend.get_json(backend.matches)

@app.route("/match/<matchid>")
def match(matchid):
    for match in backend.matches:
        if match.get_id() == matchid:
            return backend.get_json(match)

    return "Match ID not found"

@app.route("/addmatch", methods=["POST"])
def addmatch():
    if request.content_type == "application/json":
        data = request.json

        if validate_request_data(data):
            return "post success: " + str(data)
        else:
            return "post request missing essential data"

    else:
        return "Invalid content type. Please use application/json"


@app.route("/settimes")
def settimes():
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

@app.route("/newmatch")
def newmatch():
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

def validate_request_data(data):
    has_map = "map" in data
    has_zone = "zone" in data
    has_teams = "teams" in data
    #TODO: improve this 

    return has_map and has_zone and has_teams

def main():
    #start main backend loop in a thread
    loop = threading.Thread(target=backend.backend_loop)
    loop.start()

    #start flask handling in main thread
    app.run()
    backend.threadcontrol.set()
    loop.join()
    

if __name__ == "__main__":
    main()

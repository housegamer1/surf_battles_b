from flask import Flask
import backend
import threading
import datetime

app = Flask(__name__)


@app.route("/")
def hello_world():
    return backend.get_json(backend.matches[0].get_leaderboard())

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

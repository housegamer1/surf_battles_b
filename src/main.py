from flask import Flask
import backend
import threading
import datetime
import atexit

app = Flask(__name__)


@app.route("/")
def hello_world():
    return backend.get_json(backend.matches)

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

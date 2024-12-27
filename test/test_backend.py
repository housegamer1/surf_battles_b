import src.backend
import datetime

#im no test engineer, go easy on me monkaS

def test_record(): #wowee much useful
    now = datetime.datetime.now(datetime.timezone.utc)
    time = 60
    map = "surf_blackheart"
    zone = 0
    rec = src.backend.Record(time, now, map, zone)

    assert rec.get_time() == time
    assert rec.get_timestamp() == now
    assert rec.get_map() == map
    assert rec.get_zone() == zone

def test_add_time():
    id = 37964988
    now = datetime.datetime.now(datetime.timezone.utc)
    time = 60
    map = "surf_blackheart"
    zone = 0

    player = src.backend.Player(id)

    assert player.get_id() == id
    assert player.get_records() == []
    assert player.get_personal_best(map, zone) == None

    player.add_time(time, now, map, zone)
    assert len(player.get_records()) == 1
    assert player.get_personal_best(map, zone) == time
    
    
def test_team():
    player1_id = 921269561
    player2_id = 287362850
    player3_id = 106196572
    player1 = src.backend.Player(player1_id)
    player2 = src.backend.Player(player2_id)
    player3 = src.backend.Player(player3_id)

    team = src.backend.Team("Pakistan", [player1, player2])

    assert len(team.get_players()) == 2
    assert player1 in team.get_players() and player2 in team.get_players() and player3 not in team.get_players()

    team.add_player(player3)

    assert len(team.get_players()) == 3
    assert player1 in team.get_players() and player2 in team.get_players() and player3 in team.get_players()

    team.remove_player(player2)

    assert len(team.get_players()) == 2
    assert player1 in team.get_players() and player2 not in team.get_players() and player3 in team.get_players()


def test_match():
    #TODO add a test with 3 or more teams where one has less completions to see if the time sorting is kept once we apply the completions sorting
    player1_id = 38142345
    player2_id = 37964988
    player3_id = 246208267
    player4_id = 58229111
    player1 = src.backend.Player(player1_id)
    player2 = src.backend.Player(player2_id)
    player3 = src.backend.Player(player3_id)
    player4 = src.backend.Player(player4_id)

    team1 = src.backend.Team("Sweden", [player1, player4])
    team2 = src.backend.Team("Germany", [player2, player3])

    starttime = datetime.datetime.now(datetime.timezone.utc)
    duration = 10 #minutes
    teams = [team1, team2]
    surfmap = "surf_njv"
    zone = 4

    match = src.backend.Match(starttime, duration, surfmap, zone, teams)

    assert match.get_id() == "38142345_58229111_37964988_246208267_" + str(starttime)
    assert match.get_leading_team() == None
    assert match.get_leaderboard() == None

    match.determine_leading_team() # calling the function here just to see what happens when no pbs are set. any outcome is random as it sorts 2 entries with time 0 so im not gonna assert anything

    newtime = datetime.datetime.now(datetime.timezone.utc) #program wont add times unless they are more recent than the match start
    player1.add_time(50, newtime, surfmap, zone)
    player2.add_time(60, newtime, surfmap, zone)
    match.determine_leading_team()

    team1_dict = {
                "name": "Sweden",
                "times_set": 1,
                "sum_time": 50
            }
    team2_dict = {
                "name": "Germany",
                "times_set": 1,
                "sum_time": 60
            }

    assert match.get_leading_team() == team1_dict
    assert len(match.get_leaderboard()) == 2
    assert match.get_leaderboard()[1] == team2_dict

    player3.add_time(60, newtime, surfmap, zone)
    match.determine_leading_team()
    team2_dict = {
                "name": "Germany",
                "times_set": 2,
                "sum_time": 120
            }
    
    assert match.get_leading_team() == team2_dict
    assert len(match.get_leaderboard()) == 2
    assert match.get_leaderboard()[1] == team1_dict


    
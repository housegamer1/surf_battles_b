import src.backend
import datetime
import threading
import time
import json


#im no test engineer, go easy on me monkaS

def test_record(): #wowee much useful
    now = datetime.datetime.now(datetime.timezone.utc)
    time = 60
    map = "surf_blackheart"
    zone = 0
    rec = src.backend.Record(time, now, map, zone, 0, 0, 0)

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
    assert player.get_personal_best(map, zone) == "No time on match map yet"

    player.add_time(time, now, map, zone, now, 0, 0, 0)
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
    player1_id = 38142345
    player2_id = 58229111
    player3_id = 37964988
    player4_id = 246208267
    player5_id = 44534061
    player6_id = 340810357
    player1 = src.backend.Player(player1_id)
    player2 = src.backend.Player(player2_id)
    player3 = src.backend.Player(player3_id)
    player4 = src.backend.Player(player4_id)
    player5 = src.backend.Player(player5_id)
    player6 = src.backend.Player(player6_id)
    team1 = src.backend.Team("Sweden", [player1, player2])
    team2 = src.backend.Team("Germany", [player3, player4])
    team3 = src.backend.Team("Finland", [player5, player6])

    starttime = datetime.datetime.now(datetime.timezone.utc)
    duration = 10 #minutes
    teams = [team1, team2, team3]
    surfmap = "surf_njv"
    zone = 4

    match = src.backend.Match(duration, surfmap, zone, teams)

    assert match.get_leaderboard() == None

    match.determine_leading_team() # calling the function here just to see what happens when no pbs are set. any outcome is random as it sorts 2 entries with time 0 so im not gonna assert anything

    newtime = datetime.datetime.now(datetime.timezone.utc) #program wont add times unless they are more recent than the match start
    player1.add_time(50, newtime, surfmap, zone, starttime, 0, 0, 0)
    player3.add_time(60, newtime, surfmap, zone, starttime, 0, 0, 0)
    match.determine_leading_team()

    team1_dict = {
                "team": team1,
                "times_set": 1,
                "sum_time": 50
            }
    team2_dict = {
                "team": team2,
                "times_set": 1,
                "sum_time": 60
            }

    team3_dict = {
                "team": team3,
                "times_set": 0,
                "sum_time": 0
            }

    assert len(match.get_leaderboard()["entries"]) == 3
    assert match.get_leaderboard()["leading_team"] == "Sweden"
    assert match.get_leaderboard()["entries"][0] == team1_dict
    assert match.get_leaderboard()["entries"][1] == team2_dict
    assert match.get_leaderboard()["entries"][2] == team3_dict

    player4.add_time(60, newtime, surfmap, zone, starttime, 0, 0, 0)
    match.determine_leading_team()
    team2_dict = {
                "team": team2,
                "times_set": 2,
                "sum_time": 120
            }
    
    
    assert len(match.get_leaderboard()["entries"]) == 3
    assert match.get_leaderboard()["leading_team"] == "Germany"
    assert match.get_leaderboard()["entries"][0] == team2_dict
    assert match.get_leaderboard()["entries"][1] == team1_dict
    assert match.get_leaderboard()["entries"][2] == team3_dict

    player5.add_time(50, newtime, surfmap, zone, starttime, 0, 0, 0)
    player6.add_time(50, newtime, surfmap, zone, starttime, 0, 0, 0)
    match.determine_leading_team()

    team3_dict = {
            "team": team3,
            "times_set": 2,
            "sum_time": 100
        }

    assert len(match.get_leaderboard()["entries"]) == 3
    assert match.get_leaderboard()["leading_team"] == "Finland"
    assert match.get_leaderboard()["entries"][0] == team3_dict
    assert match.get_leaderboard()["entries"][1] == team2_dict
    assert match.get_leaderboard()["entries"][2] == team1_dict


def test_multimatch():
    #should pretty much not be needed since all matches run as separate instances but doesnt hurt either
    #should i include a test where one player plays multiple matches at the same time?
    player1_id = 38142345
    player2_id = 58229111
    player3_id = 37964988
    player4_id = 246208267
    player5_id = 44534061
    player6_id = 340810357
    player1 = src.backend.Player(player1_id)
    player2 = src.backend.Player(player2_id)
    player3 = src.backend.Player(player3_id)
    player4 = src.backend.Player(player4_id)
    player5 = src.backend.Player(player5_id)
    player6 = src.backend.Player(player6_id)
    team1 = src.backend.Team("A", [player1])
    team2 = src.backend.Team("B", [player2])
    team3 = src.backend.Team("C", [player3])
    team4 = src.backend.Team("D", [player4])
    team5 = src.backend.Team("E", [player5])
    team6 = src.backend.Team("F", [player6])

    starttime = datetime.datetime.now(datetime.timezone.utc)
    duration = 10 #minutes

    teams_match1 = [team1, team2]
    teams_match2 = [team3, team4]
    teams_match3 = [team5, team6]

    surfmap_match1 = "surf_njv"
    zone_match1 = 4

    surfmap_match2 = "surf_blackheart"
    zone_match2 = 0

    surfmap_match3 = "surf_corruption"
    zone_match3 = 0

    match1 = src.backend.Match(duration, surfmap_match1, zone_match1, teams_match1)
    match2 = src.backend.Match(duration, surfmap_match2, zone_match2, teams_match2)
    match3 = src.backend.Match(duration, surfmap_match3, zone_match3, teams_match3)

    newtime = datetime.datetime.now(datetime.timezone.utc) #program wont add times unless they are more recent than the match start
    player1.add_time(10, newtime, surfmap_match1, zone_match1, starttime, 0, 0, 0)
    player2.add_time(10, newtime, surfmap_match1, zone_match1, starttime, 0, 0, 0) #player2 set the exact same time!! who is ahead? 

    player3.add_time(11, newtime, surfmap_match2, zone_match2, starttime, 0, 0, 0)
    player3.add_time(9, newtime, surfmap_match1, zone_match1, starttime, 0, 0, 0) #player3 was funny and completed another map (and its time faster than the match map he is signed up for)
    player4.add_time(10, newtime, surfmap_match2, zone_match2, starttime, 0, 0, 0)

    player5.add_time(10, newtime, surfmap_match3, zone_match3, starttime, 0, 0, 0)
    player6.add_time(11, newtime, surfmap_match3, zone_match3, starttime, 0, 0, 0)

    match1.determine_leading_team()
    match2.determine_leading_team()
    match3.determine_leading_team()

    assert match1.get_leaderboard()["leading_team"] == "It's a draw! Between A and B"
    assert match2.get_leaderboard()["leading_team"] == "D"
    assert match3.get_leaderboard()["leading_team"] == "E"

    # with open("match3_leaderboard.txt", "w") as log: #just for checking the json early on. should probably make a test for that once i have my endpoints #TODO
    #     json.dump(src.backend.get_json(match3.get_leaderboard()), log)


def test_determine_team_delta():
    player1_id = 38142345
    player2_id = 58229111
    player3_id = 37964988
    player1 = src.backend.Player(player1_id)
    player2 = src.backend.Player(player2_id)
    player3 = src.backend.Player(player3_id)
    team1 = src.backend.Team("A", [player1])
    team2 = src.backend.Team("B", [player2])
    team3 = src.backend.Team("C", [player3])

    starttime = datetime.datetime.now(datetime.timezone.utc)
    duration = 10 #minutes

    teams_match1 = [team1, team2, team3]
    surfmap_match1 = "surf_njv"
    zone_match1 = 4

    match1 = src.backend.Match(duration, surfmap_match1, zone_match1, teams_match1)

    newtime = datetime.datetime.now(datetime.timezone.utc) #program wont add times unless they are more recent than the match start
    player1.add_time(10, newtime, surfmap_match1, zone_match1, starttime, 0, 0, 0)
    player2.add_time(10.015, newtime, surfmap_match1, zone_match1, starttime, 0, 0, 0) #1tick diff
    player3.add_time(13.625, newtime, surfmap_match1, zone_match1, starttime, 0, 0, 0)

    team1_dict = {
                "team": team1,
                "times_set": 1,
                "sum_time": 10
            }
    team2_dict = {
                "team": team2,
                "times_set": 1,
                "sum_time": 10.015
            }

    team3_dict = {
                "team": team3,
                "times_set": 1,
                "sum_time": 13.625
            }

    match1.determine_leading_team() #required for determining team deltas

    assert len(match1.get_leaderboard()["entries"]) == 3
    assert match1.get_leaderboard()["leading_team"] == "A"
    assert match1.get_leaderboard()["entries"][0] == team1_dict
    assert match1.get_leaderboard()["entries"][1] == team2_dict
    assert match1.get_leaderboard()["entries"][2] == team3_dict

    match1.determine_team_delta()

    assert team1.get_diff_to_fastest_team() == 0
    assert team2.get_diff_to_fastest_team() == 0.015
    assert team3.get_diff_to_fastest_team() == 3.625


def test_determine_player_delta():
    player1_id = 38142345
    player2_id = 58229111
    player3_id = 37964988
    player4_id = 246208267
    player1 = src.backend.Player(player1_id)
    player2 = src.backend.Player(player2_id)
    player3 = src.backend.Player(player3_id)
    player4 = src.backend.Player(player4_id)
    team1 = src.backend.Team("A", [player1, player2])
    team2 = src.backend.Team("B", [player3, player4])

    starttime = datetime.datetime.now(datetime.timezone.utc)
    duration = 10 #minutes

    teams_match1 = [team1, team2]
    surfmap_match1 = "surf_njv"
    zone_match1 = 4

    match1 = src.backend.Match(duration, surfmap_match1, zone_match1, teams_match1)
    newtime = datetime.datetime.now(datetime.timezone.utc) #program wont add times unless they are more recent than the match start


    player1.add_time(None, newtime, surfmap_match1, zone_match1, starttime, 0, 0, 0)
    player2.add_time(10.015, newtime, surfmap_match1, zone_match1, starttime, 0, 0, 0)
    player3.add_time(8.75, newtime, surfmap_match1, zone_match1, starttime, 0, 0, 0)
    player4.add_time(8, newtime, surfmap_match1, zone_match1, starttime, 0, 0, 0)

    match1.determine_leading_team() #required for determining player deltas
    match1.determine_player_delta()

    assert player1.get_diff_to_fastest_player() == 999999
    assert player2.get_diff_to_fastest_player() == 2.015
    assert player3.get_diff_to_fastest_player() == 0.75
    assert player4.get_diff_to_fastest_player() == 0
    

def mock_return_from_api(*args):
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        finishes_json = """
[
    {
        "id": 358114,
        "name": "cat lol",
        "steamid": "208264715",
        "map": "surf_not_a_real_map",
        "time": 17.46875,
        "ispr": 1,
        "iswr": 1,
        "isfirstrec": 1,
        "rank": 1,
        "track": 0,
        "tier": 9,
        "date": REPLACEME,
        "finishspeed": 2849.617431640625,
        "session_mapseconds": 7219,
        "session_zoneseconds": 589,
        "session_zonestarts": 171,
        "session_levelseconds": 1998

    }
]"""
        finishes_json = finishes_json.replace("REPLACEME", '"' + timestamp + '"')
        return json.loads(finishes_json)


def test_poll_loop(mocker):
    #for some dumb reason this test fails when run with all the others at once, individually it passes
    mocker.patch.object(src.backend, "request", side_effect=mock_return_from_api)


    player1_id = 208264715
    player2_id = 58229111
    player1 = src.backend.Player(player1_id)
    player2 = src.backend.Player(player2_id)
    team1 = src.backend.Team("A", [player1])
    team2 = src.backend.Team("B", [player2])

    duration = 10 #minutes

    teams_match1 = [team1, team2]
    surfmap_match1 = "surf_not_a_real_map"
    zone_match1 = 0

    match1 = src.backend.Match(duration, surfmap_match1, zone_match1, teams_match1)
    assert match1.get_leaderboard() == None
    assert match1.get_match_status() == src.backend.MatchStatus.NOT_STARTED
    match1.set_match_status(src.backend.MatchStatus.RUNNING)

    #start main backend loop in a thread
    loop = threading.Thread(target=src.backend.backend_loop)
    loop.start()

    #do whatever we need to do
    time.sleep(3) #give the backend thread enough time to run at least one loop

    try:
        assert match1.get_leaderboard()["leading_team"] == "A"
        assert match1.get_leaderboard()["entries"][0]["times_set"] == 1
    except AssertionError: #if we dont catch this, the thread will never terminate it seems
        src.backend.threadcontrol.set()
        loop.join()
        raise #brings up the caught assertion error again

    #end the thread
    src.backend.threadcontrol.set()
    loop.join()

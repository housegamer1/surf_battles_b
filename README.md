# Surf Battles Backend #

Tool to track completions of players in Surfheaven events.<br>
Forked from https://bitbucket.org/housegamer/sh_event_timer/src/ at e5cb9f9<br>
Intended for https://github.com/sKzAy/surf_battles


## Requirements

requires python3 <br>
requires requests<br>
requires flask<br>
requires dateutil<br>


## Docker

    docker build -t surf_battles_b/backend:vX.X.X .

## Functionality
* keep track of matches while providing times set by the players (in seconds) as well as determining the leader based on (sorted by priority):
  - team with most completions on the match map&zone
  - team with the lowest combined time on the match map&zone
  - supports tie

* matches are accessed via their id
* keep track of the time difference of each team to the fastest team (in seconds)
* keep track of the time difference of each player to the fastest player (in seconds)
* keeps track of the players connection status (offline, online wrong map, online)
* track time, date, rank, ispr, iswr, map, zone of a players finish
* forwards the players name from sh api as well
* finishes are only valid if they happened after /addmatch was used to create the match
* bet i forgot something but yeah this is the basics
* match_status will be set to OVER once the specified duration is up and times will no longer be added to this match

## Endpoints
* / - GET- does nothing
* /matches -GET- returns a list of all matches and their respective info
* /match/id -GET- returns info of a specific match
* /addmatch -POST- creates a new match. expects content-type to be application/json and the body to contain map, zone, duration, teams (where teams is a list containing a name and a list of steamids for the players (compare the curl.sh helper i used to test stuff). steamid as seen in sh profile url)
* /removematch -DELETE- removes a match. expects content-type to be application/json and the body to contain the id
* /controlmatch -POST- controls the match status, can be set to NOT_STARTED, RUNNING, PAUSED, OVER. expects content-type to be application/json and the body to contain the id and set_status

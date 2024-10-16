import requests
import json
import time
import datetime
import keyboard

########################
# Player related stuff #
########################
class Player:
    id      = None
    name    = None
    records   = []

    def __init__(self, id) -> None:
        self.id = id
        self.name = request_name(id)

    def add_time(self, settime, settimestamp, map=None, zone=None):
        finish = {
            "time": settime,
            "timestamp": settimestamp #to avoid re-adding the same timestamp but allow adding the same set time
        }

        for entry in self.records:
            if entry["timestamp"] == settimestamp:
                return

        self.records.append(finish)

        finishprint = self.get_name() + " finished "
        
        if map != None:
            finishprint = finishprint + map + " "

        if zone != None:
            zone = "(map)" if str(zone) == "0" else "B" + str(zone)
            finishprint = finishprint + str(zone)

        finishprint = finishprint + " in " + pretty_print_time(settime)
        print(finishprint)

    def clear_times(self):
        self.records.clear()

    def tostring(self):
        return str(self.name) + "    " + str(self.id)
    
    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name

########################
# Config related stuff #
########################
class Config:
    players = []
    surfmap = None  #optional
    zone    = None  #optional

    def load_config(self):
        #Possibly add a config validation step here?
        #Clearly all surfers are smart and the DAU has like 120+ IQ Clueless

        with open("playerids.txt", "r") as cfgfile:
            for line in cfgfile.readlines():
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue

                elif line.startswith("map="):
                    self.surfmap = parse_map(line)
                
                elif line.startswith("zone="):
                    self.zone = parse_zone(line)

                else:
                    newplayer = True
                    for player in self.players:
                        if player.get_id() == line:
                            newplayer = False
                            break

                    if newplayer == True:
                        self.players.append(Player(line))

        cfg.print()

        global lastConfigReload
        lastConfigReload = time.time()

    def print(self):
        toprint = "================================================="
        toprint = toprint + "\nCurrent config:"

        toprint = toprint + "\nPlayers: "

        for player in self.players:
            toprint = toprint + "\n- " + player.tostring()

        if self.surfmap != None:
            toprint = toprint + "\nMap:\t" + self.surfmap
            
        if self.zone != None:
            zone = "Main Map" if self.zone == "0" else "B" + self.zone
            toprint = toprint + "\nZone:\t" + zone

        toprint = toprint + "\n================================================="
        print(toprint)


def parse_map(text : str):
    #cant be asked to make sh request to confirm the entered map exists.
    # just take whatever the user provides and trust it (surely smart)
    text = text.replace("map=", "").lower()

    if text == "":
        return None

    if text.startswith("surf"):
        return text
    else: 
        return "surf_" + text

def parse_zone(text : str):
    #cant be asked to make sh request to confirm the entered zone exists
    # just take whatever the user provides and trust it (surely smart)
    text = text.replace("zone=", "").replace("b", "").lower()

    if text == "":
        return None

    if text == "main" or text == "map":
        return "0"
    else:
        return text

def reload(arg):
    now = time.time()
    global lastConfigReload
    global cfg

    if now - lastConfigReload > 1:
        cfg.load_config()
#############
# API Calls #
#############

def request_name(id):
    endpoint = shapi + "playerinfo/" + id
    content = request(endpoint, 200)

    if content != None and len(content) == 1: #Endpoint returns [{}] for a single player
        content = content[0]

        if "name" in content:
            return content["name"]



def check_results():
    now = time.time()
    global lastResultCheck
    global cfg

    if lastResultCheck == None or now - lastResultCheck > 2:
            
        #using general api and filtering here to reduce api calls
        endpoint = shapi + "finishes"
        content = request(endpoint, 201)

        if content != None:
            for entry in content:
                
                if cfg.surfmap != None:
                    if entry["map"] != cfg.surfmap:
                        continue

                if cfg.zone != None:
                    if entry["track"] != cfg.zone:
                        continue

                for player in cfg.players:
                    if entry["steamid"] == player.get_id():
                        player.add_time(entry["time"], entry["date"], entry["map"], entry["track"])


def request(url, acceptCode):
    try:
        result = requests.get(url)
        if result.status_code == acceptCode:
            content = result.content.decode("utf-8")
            return json.loads(content)

        return None
                   
    except requests.exceptions.RequestException as e:
        print("Caught error: " + str(e))
        return None


###############
# Leaderboard #
###############

def pretty_print_time(seconds):
    #shameless inefficient yoink from my telegram bot, cba looking up a smart solution
    playerTimeAsDelta =  str(datetime.timedelta(seconds=seconds))
    if '.' in playerTimeAsDelta:
        playerTimeAsDelta = playerTimeAsDelta[:-4]
    else:
        playerTimeAsDelta = playerTimeAsDelta + ".00"

    playerTimeString = ""

    #fuck this imma format this manually
    while  playerTimeAsDelta.startswith("0"):
        if playerTimeAsDelta.startswith("0:"):
            playerTimeAsDelta = playerTimeAsDelta[2:]
        else:
            playerTimeAsDelta = playerTimeAsDelta[1:]

    if seconds >= 3600:
        playerTimeString = playerTimeAsDelta + " hours"
    elif seconds >= 60:
        playerTimeString = playerTimeAsDelta + " minutes"
    else:
        playerTimeString = playerTimeAsDelta + " seconds"

    return playerTimeString

#######################
# globals because idc #
#######################
shapi = "https://api.surfheaven.eu/api/"
lastConfigReload = None
lastResultCheck = None
cfg = Config()

###########
# Main :) #
###########
def main():

    cfg.load_config()

    #Enter main loop
    while True:
        #Check if config reload requested
        #Also detects when not in foreground....
        #keyboard.on_press_key('R', reload)
            
        
        #Periodically check api for new results
        check_results()

        #Draw leaderboard

        #reduce cpu load. response time should be good enough idc
        time.sleep(0.1)
    
    
if __name__ == "__main__":
    main()
import requests
import json

#global it, no drama idc
shapi = "https://api.surfheaven.eu/api/"

########################
# Player related stuff #
########################
class Player:
    id      = None
    name    = None
    times   = []

    def __init__(self, id) -> None:
        self.id = id
        self.name = request_name(id)

    def add_time(self, time):
        self.times.append(time)

    def clear_times(self):
        self.times.clear()

    def tostring(self):
        return str(self.name) + "\t\t" + str(self.id)

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
                    self.players.append(Player(line))

    def print(self):
        toprint = "================================================="
        toprint = toprint + "\nCurrent config:"

        toprint = toprint + "\nPlayers: "

        for player in self.players:
            toprint = toprint + "\n" + player.tostring()

        if self.surfmap != None:
            toprint = toprint + "\nMap: " + self.surfmap
            
        if self.zone != None:
            zone = "Main Map" if self.zone == "0" else "B" + self.zone
            toprint = toprint + "\nZone: " + zone

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


#############
# API Calls #
#############

def request_name(id):
    endpoint = shapi + "playerinfo/" + id

    try:
        result = requests.get(endpoint)
        if result.status_code == 200:
            content = result.content.decode("utf-8")
            contentReadable = json.loads(content)

            if len(contentReadable) == 1: #Endpoint returns [{}]
                contentReadable = contentReadable[0]

                if "name" in contentReadable:
                    return contentReadable["name"]

           
    except requests.exceptions.RequestException as e:
        print("Caught error: " + str(e))
        return None


###############
# Leaderboard #
###############


###########
# Main :) #
###########
def main():

    cfg = Config()
    cfg.load_config()
    cfg.print()

    #Enter main loop
    while True:
        exit(0)
        
        #Check if config reload requested

        #Periodically check api for new results

        #Draw leaderboard

    
    
if __name__ == "__main__":
    main()
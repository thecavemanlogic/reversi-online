import random
import json
import os
from db.util import gen_id

os.makedirs(".db", exist_ok=True)

class Player:

    players = dict()

    @staticmethod
    def get(id):
        return Player.players.get(id)
    
    @staticmethod
    def store():
        with open(".db/players.json", "w") as f:
            json.dump(list(map(
                lambda x: Player.players[x].to_json(),
                Player.players
            )), f)
        print("finished saving...")
    
    @staticmethod
    def load():
        if os.path.isfile(".db/players.json"):
            with open(".db/players.json", "r") as f:
                data = json.load(f)
                print(data)
                for player in data:
                    player = Player(data=player)
                    Player.players[player.id] = player

    def __init__(self, name=None, data=None):

        if data:
            self.id = data["id"]
            self.name = data["name"]
        else:
            self.id = gen_id(resource=Player.players)
            self.name = name or f"Guest {random.randint(1000, 9999)}"
        
        self.game_queue = []
    
    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
        }
    
    def save(self):
        Player.players[self.id] = self
        Player.store()

    def get_next_game(self):
        if len(self.game_queue) > 0:
            return self.game_queue.pop(0)
        else:
            return None

if len(Player.players) == 0:
    Player.load()